using Content.Server.Atmos.EntitySystems;
using Content.Server.Chat.Managers;
using Content.Server.Explosion.EntitySystems;
using Content.Server.NodeContainer.EntitySystems;
using Content.Server.NodeContainer.Nodes;
using Content.Server.Radiation.Systems;
using Content.Shared._DarkSpace.Reactor;
using Content.Shared.Access.Systems;
using Content.Shared.Administration.Logs;
using Content.Shared.Atmos;
using Content.Shared.Atmos.Components;
using Content.Shared.Database;
using Content.Shared.Examine;
using Content.Shared.Popups;
using Content.Shared.Verbs;
using Robust.Server.GameObjects;
using Robust.Shared.Random;
using Robust.Shared.Timing;
using Robust.Shared.Utility;

namespace Content.Server._DarkSpace.Reactor;

public sealed partial class ReactorCoreSystem : EntitySystem
{
    [Dependency] private IGameTiming _timing = default!;
    [Dependency] private IRobustRandom _random = default!;
    [Dependency] private IChatManager _chat = default!;
    [Dependency] private ISharedAdminLogManager _adminLog = default!;
    [Dependency] private AtmosphereSystem _atmos = default!;
    [Dependency] private NodeContainerSystem _nodes = default!;
    [Dependency] private RadiationSystem _radiation = default!;
    [Dependency] private ExplosionSystem _explosion = default!;
    [Dependency] private AccessReaderSystem _access = default!;
    [Dependency] private SharedPopupSystem _popup = default!;
    [Dependency] private UserInterfaceSystem _ui = default!;

    public override void Initialize()
    {
        base.Initialize();
        SubscribeLocalEvent<ReactorCoreComponent, MapInitEvent>(OnMapInit);
        SubscribeLocalEvent<ReactorCoreComponent, AtmosDeviceUpdateEvent>(OnAtmosUpdate);
        SubscribeLocalEvent<ReactorCoreComponent, ExaminedEvent>(OnExamined);
        SubscribeLocalEvent<ReactorCoreComponent, GetVerbsEvent<Verb>>(OnGetVerbs);

        Subs.BuiEvents<ReactorCoreComponent>(ReactorUiKey.Key, subs =>
        {
            subs.Event<BoundUIOpenedEvent>((ent, ref _) => UpdateUi(ent));
            subs.Event<ReactorSetRodsMessage>(OnSetRodsMessage);
            subs.Event<ReactorScramMessage>((ent, ref args) =>
            {
                if (_access.IsAllowed(args.Actor, ent))
                    Scram(ent, args.Actor);
            });
            subs.Event<ReactorResetScramMessage>((ent, ref args) =>
            {
                if (_access.IsAllowed(args.Actor, ent))
                    ResetScram(ent, args.Actor);
            });
        });
    }

    private void OnSetRodsMessage(Entity<ReactorCoreComponent> ent, ref ReactorSetRodsMessage args)
    {
        if (!_access.IsAllowed(args.Actor, ent))
        {
            _popup.PopupEntity(Loc.GetString("ds-reactor-access-denied"), ent, args.Actor);
            return;
        }

        SetRodTarget(ent, args.Target, args.Actor);
    }

    private void UpdateUi(Entity<ReactorCoreComponent> ent)
    {
        if (!_ui.IsUiOpen(ent.Owner, ReactorUiKey.Key))
            return;

        var c = ent.Comp;
        _ui.SetUiState(ent.Owner, ReactorUiKey.Key, new ReactorUiState(
            c.Power, c.NominalPower, c.KEff, c.CoreTemperature, c.CoolantTemperature,
            c.WarningTemperature, c.MeltdownTemperature, c.RodInsertion, c.TargetRodInsertion,
            c.Integrity, c.Scrammed, c.Melted, c.BatchNumber, c.PassportReproduction, c.PassportError,
            c.Size, c.Cells));
    }

    private void OnMapInit(Entity<ReactorCoreComponent> ent, ref MapInitEvent args)
    {
        var comp = ent.Comp;
        comp.Cells = ParseLayout(comp.Layout, comp.Size);

        comp.Reproduction = _random.NextFloat(comp.ReproductionMin, comp.ReproductionMax);
        comp.PassportReproduction = comp.Reproduction * (1f + _random.NextFloat(-comp.PassportError, comp.PassportError));
        comp.BatchNumber = _random.Next(1000, 9999);
    }

    public static List<ReactorCellType> ParseLayout(List<string> rows, int size)
    {
        var cells = new List<ReactorCellType>(size * size);
        for (var y = 0; y < size; y++)
        {
            var row = y < rows.Count ? rows[y] : string.Empty;
            for (var x = 0; x < size; x++)
            {
                cells.Add((x < row.Length ? row[x] : '.') switch
                {
                    'F' => ReactorCellType.Fuel,
                    'R' => ReactorCellType.Rod,
                    'G' => ReactorCellType.Graphite,
                    _ => ReactorCellType.Empty,
                });
            }
        }

        return cells;
    }

    private void OnAtmosUpdate(Entity<ReactorCoreComponent> ent, ref AtmosDeviceUpdateEvent args)
    {
        var (uid, comp) = ent;
        if (comp.Melted)
            return;

        var dt = args.dt;
        MoveRods(comp, dt);

        GasMixture? coolant = null;
        if (_nodes.TryGetNode(uid, comp.PipeName, out PipeNode? pipe) && pipe.Air.TotalMoles > 0.1f)
            coolant = pipe.Air;

        comp.CoolantTemperature = coolant?.Temperature;

        var k = ReactorPhysics.LayoutK(comp.Cells, comp.Size, comp.RodInsertion, comp.Reproduction, comp.Coefficients)
                + ReactorPhysics.ThermalFeedback(comp.CoreTemperature, comp.CoolantTemperature, comp.Coefficients);

        if (_timing.CurTime < comp.ScramSpikeEnd)
            k += comp.ScramSpikeMagnitude;

        comp.KEff = k;

        var source = k > 0f ? comp.SourcePower : 0f;
        comp.Power = ReactorPhysics.StepPower(comp.Power, k, comp.GenerationTime, dt, source, comp.MaxPower);

        var heat = comp.Power * dt;
        if (coolant != null)
        {
            var gasCapacity = _atmos.GetHeatCapacity(coolant, true);
            var moved = ReactorPhysics.HeatToCoolant(comp.CoreTemperature, coolant.Temperature, comp.Conductance, comp.CoreHeatCapacity, gasCapacity, dt);
            _atmos.AddHeat(coolant, moved);
            heat -= moved;
        }

        comp.CoreTemperature = MathF.Max(Atmospherics.TCMB, comp.CoreTemperature + heat / comp.CoreHeatCapacity);

        _radiation.SetIntensity(uid, comp.BaseRadiation + comp.RadiationPerNominal * comp.Power / comp.NominalPower);

        UpdateFailure(ent, dt);
        UpdateUi(ent);
    }

    private void MoveRods(ReactorCoreComponent comp, float dt)
    {
        var speed = comp.Scrammed ? comp.ScramRodSpeed : comp.RodSpeed;
        var delta = comp.TargetRodInsertion - comp.RodInsertion;
        comp.RodInsertion += Math.Clamp(delta, -speed * dt, speed * dt);
    }

    private void UpdateFailure(Entity<ReactorCoreComponent> ent, float dt)
    {
        var (uid, comp) = ent;

        if (!comp.WarningActive && comp.CoreTemperature > comp.WarningTemperature)
        {
            comp.WarningActive = true;
            _popup.PopupEntity(Loc.GetString("ds-reactor-warning-overheat"), uid, PopupType.LargeCaution);
            _chat.SendAdminAlert(Loc.GetString("ds-reactor-admin-overheat", ("reactor", ToPrettyString(uid)), ("temp", (int) comp.CoreTemperature)));
            _adminLog.Add(LogType.Action, LogImpact.High, $"Reactor {ToPrettyString(uid):reactor} overheated to {comp.CoreTemperature:F0} K");
        }
        else if (comp.WarningActive && comp.CoreTemperature < comp.WarningTemperature - 100f)
        {
            comp.WarningActive = false;
        }

        if (comp.CoreTemperature <= comp.MeltdownTemperature)
            return;

        var excess = (comp.CoreTemperature - comp.MeltdownTemperature) / 100f;
        comp.Integrity -= comp.IntegrityLossRate * (1f + excess) * dt;
        if (comp.Integrity <= 0f)
            Meltdown(ent);
    }

    private void Meltdown(Entity<ReactorCoreComponent> ent)
    {
        var (uid, comp) = ent;
        comp.Melted = true;
        comp.Integrity = 0f;
        comp.Power = 0f;

        _chat.SendAdminAlert(Loc.GetString("ds-reactor-admin-meltdown", ("reactor", ToPrettyString(uid))));
        _adminLog.Add(LogType.Explosion, LogImpact.Extreme, $"Reactor {ToPrettyString(uid):reactor} melted down");

        var coords = Transform(uid).Coordinates;
        Spawn(comp.CoriumPrototype, coords);
        UpdateUi(ent);
        _explosion.QueueExplosion(uid, "Default", comp.MeltdownExplosionIntensity, 3f, 30f, addLog: false);
    }

    public void SetRodTarget(Entity<ReactorCoreComponent> ent, float target, EntityUid? user)
    {
        if (ent.Comp.Scrammed)
            return;

        ent.Comp.TargetRodInsertion = Math.Clamp(target, 0f, 1f);
        if (user != null)
            _adminLog.Add(LogType.Action, LogImpact.Medium, $"{ToPrettyString(user.Value):user} set rods of {ToPrettyString(ent):reactor} to {ent.Comp.TargetRodInsertion:P0}");
        UpdateUi(ent);
    }

    /// <summary>
    /// AZ-5: all rods go down. The graphite displacers enter first, so reactivity briefly rises.
    /// </summary>
    public void Scram(Entity<ReactorCoreComponent> ent, EntityUid? user)
    {
        var comp = ent.Comp;
        if (comp.Scrammed)
            return;

        comp.Scrammed = true;
        comp.TargetRodInsertion = 1f;
        comp.ScramSpikeMagnitude = comp.ScramSpike * (1f - comp.RodInsertion);
        comp.ScramSpikeEnd = _timing.CurTime + comp.ScramSpikeDuration;

        _popup.PopupEntity(Loc.GetString("ds-reactor-scram"), ent, PopupType.LargeCaution);
        _adminLog.Add(LogType.Action, LogImpact.High, $"{ToPrettyString(user):user} pressed AZ-5 on {ToPrettyString(ent):reactor} at {comp.Power / 1000f:F0} kW");
    }

    public void ResetScram(Entity<ReactorCoreComponent> ent, EntityUid? user)
    {
        ent.Comp.Scrammed = false;
        _adminLog.Add(LogType.Action, LogImpact.Medium, $"{ToPrettyString(user):user} reset AZ-5 on {ToPrettyString(ent):reactor}");
    }

    private void OnGetVerbs(Entity<ReactorCoreComponent> ent, ref GetVerbsEvent<Verb> args)
    {
        if (!args.CanAccess || !args.CanInteract || ent.Comp.Melted)
            return;

        var user = args.User;
        if (!_access.IsAllowed(user, ent))
            return;

        var comp = ent.Comp;
        var category = new VerbCategory("ds-reactor-verb-category", null);

        args.Verbs.Add(new Verb
        {
            Text = Loc.GetString("ds-reactor-verb-rods-up"),
            Category = category,
            Priority = 3,
            Disabled = comp.Scrammed,
            Act = () => SetRodTarget(ent, comp.TargetRodInsertion - comp.RodStep, user),
        });

        args.Verbs.Add(new Verb
        {
            Text = Loc.GetString("ds-reactor-verb-rods-down"),
            Category = category,
            Priority = 2,
            Disabled = comp.Scrammed,
            Act = () => SetRodTarget(ent, comp.TargetRodInsertion + comp.RodStep, user),
        });

        if (comp.Scrammed)
        {
            args.Verbs.Add(new Verb
            {
                Text = Loc.GetString("ds-reactor-verb-reset"),
                Category = category,
                Priority = 1,
                Act = () => ResetScram(ent, user),
            });
        }
        else
        {
            args.Verbs.Add(new Verb
            {
                Text = Loc.GetString("ds-reactor-verb-scram"),
                Category = category,
                Priority = 1,
                Impact = LogImpact.High,
                ConfirmationPopup = true,
                Act = () => Scram(ent, user),
            });
        }
    }

    private void OnExamined(Entity<ReactorCoreComponent> ent, ref ExaminedEvent args)
    {
        if (!args.IsInDetailsRange)
            return;

        var comp = ent.Comp;
        using (args.PushGroup(nameof(ReactorCoreComponent)))
        {
            if (comp.Melted)
            {
                args.PushMarkup(Loc.GetString("ds-reactor-examine-melted"));
                return;
            }

            args.PushMarkup(Loc.GetString("ds-reactor-examine-passport",
                ("batch", comp.BatchNumber),
                ("k", comp.PassportReproduction.ToString("F3")),
                ("error", (int) MathF.Round(comp.PassportError * 100))));
            args.PushMarkup(Loc.GetString("ds-reactor-examine-power",
                ("power", (comp.Power / 1000f).ToString("F1")),
                ("keff", comp.KEff.ToString("F4"))));
            args.PushMarkup(Loc.GetString("ds-reactor-examine-temp",
                ("core", (int) comp.CoreTemperature),
                ("coolant", comp.CoolantTemperature is { } t ? ((int) t).ToString() : "—"),
                ("limit", (int) comp.MeltdownTemperature)));
            args.PushMarkup(Loc.GetString("ds-reactor-examine-rods",
                ("rods", (int) MathF.Round(comp.RodInsertion * 100)),
                ("target", (int) MathF.Round(comp.TargetRodInsertion * 100)),
                ("integrity", (int) comp.Integrity)));

            if (comp.Scrammed)
                args.PushMarkup(Loc.GetString("ds-reactor-examine-scrammed"));

            args.PushMarkup(Loc.GetString("ds-reactor-examine-layout", ("layout", FormatLayout(comp))));
        }
    }

    private static string FormatLayout(ReactorCoreComponent comp)
    {
        var sb = new System.Text.StringBuilder();
        for (var y = 0; y < comp.Size; y++)
        {
            if (y > 0)
                sb.Append('\n');
            for (var x = 0; x < comp.Size; x++)
            {
                sb.Append(comp.Cells[y * comp.Size + x] switch
                {
                    ReactorCellType.Fuel => 'Т',
                    ReactorCellType.Rod => 'С',
                    ReactorCellType.Graphite => 'Г',
                    _ => '·',
                });
            }
        }

        return FormattedMessage.EscapeText(sb.ToString());
    }
}
