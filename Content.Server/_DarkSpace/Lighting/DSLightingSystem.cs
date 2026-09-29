using Content.Server.GameTicking;
using Content.Server.Light.EntitySystems;
using Content.Shared.GameTicking;
using Content.Shared.Light.Components;
using Content.Shared.Light.EntitySystems;
using Robust.Shared.Configuration;
using Robust.Shared.Containers;
using Robust.Shared.Random;
using Robust.Shared.Timing;

namespace Content.Server._DarkSpace.Lighting;

/// <summary>
/// Makes station lamps dimmer and warmer, and makes some of them misbehave at random:
/// stutter, flicker for a long time, die out and click back on, or sag into a brownout.
/// Which lamps are faulty and how often things go wrong is rolled anew every round.
/// </summary>
public sealed partial class DSLightingSystem : EntitySystem
{
    [Dependency] private IConfigurationManager _cfg = default!;
    [Dependency] private IGameTiming _timing = default!;
    [Dependency] private IRobustRandom _random = default!;
    [Dependency] private EntityLookupSystem _lookup = default!;
    [Dependency] private PoweredLightSystem _poweredLight = default!;
    [Dependency] private SharedLightBulbSystem _bulb = default!;
    [Dependency] private SharedPointLightSystem _pointLight = default!;
    [Dependency] private SharedContainerSystem _container = default!;

    // Chance that a fault picks a random healthy lamp instead of a faulty one.
    private const float HealthyLampChance = 0.15f;
    // Chance that a fault spreads to nearby lamps, like a bad circuit in a corridor.
    private const float CascadeChance = 0.12f;
    private const float CascadeRange = 5f;

    private float _energyMult;
    private float _radiusMult;
    private Color? _tint;
    private float _tintStrength;
    private bool _faultsEnabled;
    private float _faultyChance;
    private float _faultInterval;

    /// <summary>
    /// Rolled every round: some rounds the station wiring is calmer, some rounds it is falling apart.
    /// </summary>
    private float _roundIntensity = 1f;
    private TimeSpan _nextFault;

    private bool _rollFaulty;
    private readonly HashSet<EntityUid> _rolled = new();
    private readonly List<EntityUid> _faulty = new();
    private readonly List<EntityUid> _healthy = new();
    private readonly HashSet<Entity<PoweredLightComponent>> _nearby = new();

    public override void Initialize()
    {
        base.Initialize();

        SubscribeLocalEvent<LightBulbComponent, MapInitEvent>(OnBulbMapInit);
        SubscribeLocalEvent<PostGameMapLoad>(_ => _rollFaulty = true);
        SubscribeLocalEvent<RoundRestartCleanupEvent>(_ => RollRound());

        Subs.CVar(_cfg, DSLightingCVars.EnergyMultiplier, v => _energyMult = v, true);
        Subs.CVar(_cfg, DSLightingCVars.RadiusMultiplier, v => _radiusMult = v, true);
        Subs.CVar(_cfg, DSLightingCVars.Tint, v => _tint = Color.TryFromHex(v, out var c) ? c : null, true);
        Subs.CVar(_cfg, DSLightingCVars.TintStrength, v => _tintStrength = v, true);
        Subs.CVar(_cfg, DSLightingCVars.FaultsEnabled, v => _faultsEnabled = v, true);
        Subs.CVar(_cfg, DSLightingCVars.FaultyChance, v => _faultyChance = v, true);
        Subs.CVar(_cfg, DSLightingCVars.FaultInterval, v => _faultInterval = v, true);

        RollRound();
    }

    private void RollRound()
    {
        _roundIntensity = _random.NextFloat(0.5f, 1.6f);
        _rolled.Clear();
        _nextFault = _timing.CurTime + TimeSpan.FromSeconds(30);
    }

    #region Dimming

    private void OnBulbMapInit(Entity<LightBulbComponent> ent, ref MapInitEvent args)
    {
        var bulb = ent.Comp;
        bulb.LightEnergy *= _energyMult;
        bulb.LightRadius *= _radiusMult;

        if (_tint is { } tint && _tintStrength > 0f)
            _bulb.SetColor(ent, Color.InterpolateBetween(bulb.Color, tint, _tintStrength), bulb);

        // Bulbs spawned straight into a lit fixture may already have lit it with the old values.
        if (bulb.State == LightBulbState.Normal
            && _container.TryGetContainingContainer((ent, null, null), out var container)
            && TryComp<PoweredLightComponent>(container.Owner, out var fixture)
            && fixture.CurrentLit
            && _pointLight.TryGetLight(container.Owner, out var pointLight))
        {
            _pointLight.SetEnergy(container.Owner, bulb.LightEnergy, pointLight);
            _pointLight.SetRadius(container.Owner, bulb.LightRadius, pointLight);
            _pointLight.SetColor(container.Owner, bulb.Color, pointLight);
        }
    }

    #endregion

    #region Faults

    /// <summary>
    /// Picks which lamps on freshly loaded maps are faulty. PoweredLight's MapInit is taken upstream, so this runs
    /// once on the first tick after a game map loads.
    /// </summary>
    private void RollFaultyLamps()
    {
        _rollFaulty = false;

        var query = EntityQueryEnumerator<PoweredLightComponent>();
        while (query.MoveNext(out var uid, out var light))
        {
            if (!_rolled.Add(uid) || !_random.Prob(_faultyChance))
                continue;

            // Most faulty lamps are only a little off; a few are properly dying.
            var severity = MathF.Pow(_random.NextFloat(), 2f) * 0.9f + 0.1f;
            EnsureComp<DSFaultyLightComponent>(uid).Severity = severity;

            // The worst ones flicker nonstop, the way upstream aged tubes do.
            if (severity > 0.85f && light.BulbType == LightBulbType.Tube)
                EnsureComp<BlinkingPoweredLightComponent>(uid);
        }
    }

    public override void Update(float frameTime)
    {
        base.Update(frameTime);

        if (_rollFaulty)
            RollFaultyLamps();

        var now = _timing.CurTime;

        var active = EntityQueryEnumerator<DSLightFaultComponent>();
        while (active.MoveNext(out var uid, out var fault))
        {
            if (now >= fault.EndTime)
                EndFault(uid, fault);
        }

        if (!_faultsEnabled || now < _nextFault)
            return;

        // Exponential-ish spacing so faults come in irregular bursts and lulls.
        var mean = _faultInterval / MathF.Max(_roundIntensity, 0.05f);
        var wait = -MathF.Log(1f - _random.NextFloat() * 0.95f) * mean;
        _nextFault = now + TimeSpan.FromSeconds(Math.Clamp(wait, 0.5f, mean * 4f));

        if (PickLamp() is not { } lamp)
            return;

        var severity = CompOrNull<DSFaultyLightComponent>(lamp)?.Severity ?? 0.2f;
        var type = PickFault(severity);
        StartFault(lamp, type, severity);

        if (!_random.Prob(CascadeChance))
            return;

        _nearby.Clear();
        _lookup.GetEntitiesInRange(Transform(lamp).Coordinates, CascadeRange, _nearby);
        foreach (var other in _nearby)
        {
            if (other.Owner != lamp && _random.Prob(0.6f))
                StartFault(other, type, severity);
        }
    }

    private EntityUid? PickLamp()
    {
        _faulty.Clear();
        _healthy.Clear();

        var query = EntityQueryEnumerator<PoweredLightComponent>();
        while (query.MoveNext(out var uid, out var light))
        {
            if (!light.CurrentLit || HasComp<DSLightFaultComponent>(uid) || HasComp<BlinkingPoweredLightComponent>(uid))
                continue;

            if (TryComp<DSFaultyLightComponent>(uid, out var faulty))
            {
                // Add worse lamps more than once so they get picked more often.
                for (var i = 0; i < 1 + (int) (faulty.Severity * 4); i++)
                    _faulty.Add(uid);
            }
            else
            {
                _healthy.Add(uid);
            }
        }

        if (_healthy.Count > 0 && (_faulty.Count == 0 || _random.Prob(HealthyLampChance)))
            return _random.Pick(_healthy);

        return _faulty.Count > 0 ? _random.Pick(_faulty) : null;
    }

    private DSLightFault PickFault(float severity)
    {
        var roll = _random.NextFloat();
        // Healthy lamps mostly just stutter; bad ones die out and sag more.
        if (roll < 0.55f - severity * 0.25f)
            return DSLightFault.Stutter;
        if (roll < 0.75f - severity * 0.1f)
            return DSLightFault.Brownout;
        if (roll < 0.9f)
            return DSLightFault.Flicker;
        return DSLightFault.DieOut;
    }

    private void StartFault(EntityUid uid, DSLightFault type, float severity)
    {
        if (!TryComp<PoweredLightComponent>(uid, out var light) || !light.CurrentLit || HasComp<DSLightFaultComponent>(uid))
            return;

        var now = _timing.CurTime;
        var fault = new DSLightFaultComponent { Fault = type };

        switch (type)
        {
            case DSLightFault.Stutter:
            case DSLightFault.Flicker:
                var duration = type == DSLightFault.Stutter
                    ? _random.NextFloat(0.8f, 3f)
                    : _random.NextFloat(6f, 12f + severity * 25f);
                var blinking = EnsureComp<BlinkingPoweredLightComponent>(uid);
                blinking.StopBlinkingTime = now + TimeSpan.FromSeconds(duration);
                Dirty(uid, blinking);
                fault.EndTime = now + TimeSpan.FromSeconds(duration);
                break;

            case DSLightFault.DieOut:
                _poweredLight.SetState(uid, false, light);
                fault.EndTime = now + TimeSpan.FromSeconds(_random.NextFloat(2f, 6f + severity * 20f));
                break;

            case DSLightFault.Brownout:
                if (!_pointLight.TryGetLight(uid, out var pointLight))
                    return;
                fault.OriginalEnergy = pointLight.Energy;
                fault.DimmedEnergy = pointLight.Energy * _random.NextFloat(0.2f, 0.5f);
                _pointLight.SetEnergy(uid, fault.DimmedEnergy, pointLight);
                fault.EndTime = now + TimeSpan.FromSeconds(_random.NextFloat(4f, 10f + severity * 30f));
                break;
        }

        AddComp(uid, fault);
    }

    private void EndFault(EntityUid uid, DSLightFaultComponent fault)
    {
        switch (fault.Fault)
        {
            case DSLightFault.DieOut:
                // Only switch it back if nobody else touched it; a restored lamp clicks and hums back on.
                if (TryComp<PoweredLightComponent>(uid, out var light) && !light.On)
                    _poweredLight.SetState(uid, true, light);
                break;

            case DSLightFault.Brownout:
                if (_pointLight.TryGetLight(uid, out var pointLight)
                    && MathHelper.CloseTo(pointLight.Energy, fault.DimmedEnergy))
                {
                    _pointLight.SetEnergy(uid, fault.OriginalEnergy, pointLight);
                }
                break;
        }

        RemCompDeferred<DSLightFaultComponent>(uid);
    }

    #endregion
}
