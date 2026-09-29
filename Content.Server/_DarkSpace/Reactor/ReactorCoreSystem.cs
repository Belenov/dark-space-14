using System.Linq;
using Content.Server.Atmos.EntitySystems;
using Content.Server.Chat.Managers;
using Content.Server.Explosion.EntitySystems;
using Content.Server.NodeContainer.EntitySystems;
using Content.Server.NodeContainer.Nodes;
using Content.Server.Radiation.Systems;
using Content.Shared._DarkSpace.Reactor;
using Content.Shared.Administration.Logs;
using Content.Shared.Atmos;
using Content.Shared.Atmos.Components;
using Content.Shared.Containers.ItemSlots;
using Content.Shared.Database;
using Content.Shared.Examine;
using Content.Shared.Popups;
using Robust.Server.GameObjects;
using Robust.Shared.Map.Components;
using Robust.Shared.Random;
using Robust.Shared.Timing;

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
    [Dependency] private SharedPopupSystem _popup = default!;
    [Dependency] private ItemSlotsSystem _slots = default!;
    [Dependency] private SharedMapSystem _map = default!;
    [Dependency] private AppearanceSystem _appearance = default!;
    [Dependency] private ReactorConsoleSystem _console = default!;

    public override void Initialize()
    {
        base.Initialize();
        SubscribeLocalEvent<ReactorCoreComponent, MapInitEvent>(OnMapInit);
        SubscribeLocalEvent<ReactorCoreComponent, AtmosDeviceUpdateEvent>(OnAtmosUpdate);
        SubscribeLocalEvent<ReactorCoreComponent, ExaminedEvent>(OnExamined);
    }

    private void OnMapInit(Entity<ReactorCoreComponent> ent, ref MapInitEvent args)
    {
        var comp = ent.Comp;
        comp.Reproduction = _random.NextFloat(comp.ReproductionMin, comp.ReproductionMax);
        comp.PassportReproduction = comp.Reproduction * (1f + _random.NextFloat(-comp.PassportError, comp.PassportError));
        comp.BatchNumber = _random.Next(1000, 9999);

        if (comp.Layout.Count > 0)
            SpawnMissingChannels(ent);

        RefreshChannels(ent);
    }

    /// <summary>
    /// Parses a layout string grid. Unknown characters and missing cells are empty channels.
    /// </summary>
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

    private bool TryGetGridTile(EntityUid uid, out Entity<MapGridComponent> grid, out Vector2i tile)
    {
        grid = default;
        tile = default;
        var xform = Transform(uid);
        if (xform.GridUid is not { } gridUid || !TryComp<MapGridComponent>(gridUid, out var gridComp))
            return false;

        grid = (gridUid, gridComp);
        tile = _map.TileIndicesFor(grid, xform.Coordinates);
        return true;
    }

    /// <summary>
    /// Row y = 0 is the north edge of the lid, so the layout strings read like the map.
    /// </summary>
    private static Vector2i CellTile(Vector2i center, int size, int x, int y)
    {
        var half = size / 2;
        return center + new Vector2i(x - half, half - y);
    }

    private EntityUid? FindChannel(Entity<MapGridComponent> grid, Vector2i tile)
    {
        var anchored = _map.GetAnchoredEntities(grid, tile);
        while (anchored.MoveNext(out var uid))
        {
            if (uid != null && HasComp<ReactorChannelComponent>(uid.Value))
                return uid;
        }

        return null;
    }

    private void SpawnMissingChannels(Entity<ReactorCoreComponent> ent)
    {
        var comp = ent.Comp;
        if (!TryGetGridTile(ent, out var grid, out var center))
            return;

        var layout = ParseLayout(comp.Layout, comp.Size);
        for (var y = 0; y < comp.Size; y++)
        {
            for (var x = 0; x < comp.Size; x++)
            {
                var tile = CellTile(center, comp.Size, x, y);
                if (FindChannel(grid, tile) != null)
                    continue;

                var channel = Spawn(comp.ChannelPrototype, _map.GridTileToLocal(grid, grid, tile));
                if (!comp.AssemblyPrototypes.TryGetValue(layout[y * comp.Size + x], out var proto)
                    || !TryComp<ReactorChannelComponent>(channel, out var channelComp))
                    continue;

                var assembly = Spawn(proto, Transform(channel).Coordinates);
                if (!_slots.TryInsert(channel, channelComp.SlotId, assembly, null))
                    Del(assembly);
            }
        }
    }

    /// <summary>
    /// Re-reads every channel of the lid. Cheap enough to run each atmos tick.
    /// </summary>
    private void RefreshChannels(Entity<ReactorCoreComponent> ent)
    {
        var comp = ent.Comp;
        var count = comp.Size * comp.Size;
        comp.Cells.Clear();
        comp.Channels.Clear();

        if (!TryGetGridTile(ent, out var grid, out var center))
        {
            for (var i = 0; i < count; i++)
            {
                comp.Cells.Add(ReactorCellType.Empty);
                comp.Channels.Add(null);
            }

            return;
        }

        for (var y = 0; y < comp.Size; y++)
        {
            for (var x = 0; x < comp.Size; x++)
            {
                var channel = FindChannel(grid, CellTile(center, comp.Size, x, y));
                comp.Channels.Add(channel);

                var type = ReactorCellType.Empty;
                if (channel != null
                    && TryComp<ReactorChannelComponent>(channel, out var channelComp)
                    && _slots.GetItemOrNull(channel.Value, channelComp.SlotId) is { } item
                    && TryComp<ReactorAssemblyComponent>(item, out var assembly))
                {
                    type = assembly.CellType;
                }

                comp.Cells.Add(type);
            }
        }
    }

    private void OnAtmosUpdate(Entity<ReactorCoreComponent> ent, ref AtmosDeviceUpdateEvent args)
    {
        var (uid, comp) = ent;
        if (comp.Melted)
            return;

        var dt = args.dt;
        RefreshChannels(ent);
        MoveRods(comp, dt);

        GasMixture? coolant = null;
        if (_nodes.TryGetNode(uid, comp.PipeName, out PipeNode? pipe) && pipe.Air.TotalMoles > 0.1f)
            coolant = pipe.Air;

        comp.CoolantTemperature = coolant?.Temperature;

        var factors = ReactorPhysics.CellFactors(comp.Cells, comp.Size, comp.RodInsertion, comp.Coefficients);
        var k = ReactorPhysics.LayoutK(comp.Cells, factors, comp.Reproduction, comp.Coefficients)
                + ReactorPhysics.ThermalFeedback(comp.CoreTemperature, comp.CoolantTemperature, comp.Coefficients);

        if (_timing.CurTime < comp.ScramSpikeEnd)
            k += comp.ScramSpikeMagnitude;

        comp.KEff = k;

        var hasFuel = comp.Cells.Contains(ReactorCellType.Fuel);
        var source = hasFuel ? comp.SourcePower : 0f;
        comp.Power = hasFuel
            ? ReactorPhysics.StepPower(comp.Power, k, comp.GenerationTime, dt, source, comp.MaxPower)
            : 0f;

        UpdateFlux(comp, factors);

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
        UpdateVisuals(ent);
        _console.UpdateLinkedConsoles(ent);
    }

    private void UpdateFlux(ReactorCoreComponent comp, float[] factors)
    {
        var total = 0f;
        foreach (var f in factors)
            total += f;

        comp.Flux.Clear();
        for (var i = 0; i < factors.Length; i++)
            comp.Flux.Add(total > 0f ? comp.Power * factors[i] / total : 0f);
    }

    private void MoveRods(ReactorCoreComponent comp, float dt)
    {
        var speed = comp.Scrammed ? comp.ScramRodSpeed : comp.RodSpeed;
        var delta = comp.TargetRodInsertion - comp.RodInsertion;
        comp.RodInsertion += Math.Clamp(delta, -speed * dt, speed * dt);
    }

    public ReactorCoreState GetState(ReactorCoreComponent comp)
    {
        if (comp.Melted)
            return ReactorCoreState.Wrecked;
        if (comp.CoreTemperature > comp.WarningTemperature)
            return ReactorCoreState.Critical;
        if (comp.CoreTemperature > comp.WarningTemperature - 300f)
            return ReactorCoreState.Hot;
        if (comp.Power >= comp.NominalPower * 0.3f)
            return ReactorCoreState.Nominal;
        if (comp.Power >= comp.NominalPower * 0.01f)
            return ReactorCoreState.Low;
        return ReactorCoreState.Off;
    }

    private void UpdateVisuals(Entity<ReactorCoreComponent> ent)
    {
        var comp = ent.Comp;
        _appearance.SetData(ent, ReactorCoreVisuals.State, GetState(comp));
        _appearance.SetData(ent, ReactorCoreVisuals.Cracks, comp.Integrity switch
        {
            >= 90f => 0,
            >= 50f => 1,
            >= 25f => 2,
            _ => 3,
        });
        _appearance.SetData(ent, ReactorCoreVisuals.Scram, comp.Scrammed);

        // Channel glow is relative to a nominal channel so the lid lights up as the reactor climbs.
        var perChannelNominal = comp.NominalPower / Math.Max(1, comp.Cells.Count(c => c == ReactorCellType.Fuel));
        for (var i = 0; i < comp.Channels.Count; i++)
        {
            if (comp.Channels[i] is not { } channel)
                continue;

            var level = i < comp.Flux.Count ? (int) Math.Clamp(MathF.Ceiling(comp.Flux[i] / perChannelNominal * 2f), 0f, 4f) : 0;
            _appearance.SetData(channel, ReactorChannelVisuals.Contents, comp.Cells[i]);
            _appearance.SetData(channel, ReactorChannelVisuals.Flux, level);
        }
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

        Spawn(comp.CoriumPrototype, Transform(uid).Coordinates);
        _explosion.QueueExplosion(uid, "Default", comp.MeltdownExplosionIntensity, 3f, 30f, addLog: false);
        UpdateVisuals(ent);
        _console.UpdateLinkedConsoles(ent);
    }

    public void SetRodTarget(Entity<ReactorCoreComponent> ent, float target, EntityUid? user)
    {
        if (ent.Comp.Scrammed || ent.Comp.Melted)
            return;

        ent.Comp.TargetRodInsertion = Math.Clamp(target, 0f, 1f);
        if (user != null)
            _adminLog.Add(LogType.Action, LogImpact.Medium, $"{ToPrettyString(user.Value):user} set rods of {ToPrettyString(ent):reactor} to {ent.Comp.TargetRodInsertion:P0}");
        _console.UpdateLinkedConsoles(ent);
    }

    /// <summary>
    /// AZ-5: all rods go down. The graphite displacers enter first, so reactivity briefly rises.
    /// </summary>
    public void Scram(Entity<ReactorCoreComponent> ent, EntityUid? user)
    {
        var comp = ent.Comp;
        if (comp.Scrammed || comp.Melted)
            return;

        comp.Scrammed = true;
        comp.TargetRodInsertion = 1f;
        comp.ScramSpikeMagnitude = comp.ScramSpike * (1f - comp.RodInsertion);
        comp.ScramSpikeEnd = _timing.CurTime + comp.ScramSpikeDuration;

        _popup.PopupEntity(Loc.GetString("ds-reactor-scram"), ent, PopupType.LargeCaution);
        _adminLog.Add(LogType.Action, LogImpact.High, $"{ToPrettyString(user):user} pressed AZ-5 on {ToPrettyString(ent):reactor} at {comp.Power / 1000f:F0} kW");
        _console.UpdateLinkedConsoles(ent);
    }

    public void ResetScram(Entity<ReactorCoreComponent> ent, EntityUid? user)
    {
        ent.Comp.Scrammed = false;
        _adminLog.Add(LogType.Action, LogImpact.Medium, $"{ToPrettyString(user):user} reset AZ-5 on {ToPrettyString(ent):reactor}");
        _console.UpdateLinkedConsoles(ent);
    }

    public ReactorUiState BuildUiState(ReactorCoreComponent c)
    {
        return new ReactorUiState(
            c.Power, c.NominalPower, c.KEff, c.CoreTemperature, c.CoolantTemperature,
            c.WarningTemperature, c.MeltdownTemperature, c.RodInsertion, c.TargetRodInsertion,
            c.Integrity, c.Scrammed, c.Melted, c.BatchNumber, c.PassportReproduction, c.PassportError,
            c.Size, new List<ReactorCellType>(c.Cells), new List<float>(c.Flux), true);
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

            args.PushMarkup(Loc.GetString("ds-reactor-examine-power",
                ("power", (comp.Power / 1000f).ToString("F1")),
                ("keff", comp.KEff.ToString("F4"))));
            args.PushMarkup(Loc.GetString("ds-reactor-examine-temp",
                ("core", (int) comp.CoreTemperature),
                ("coolant", comp.CoolantTemperature is { } t ? ((int) t).ToString() : "—"),
                ("limit", (int) comp.MeltdownTemperature)));
        }
    }
}
