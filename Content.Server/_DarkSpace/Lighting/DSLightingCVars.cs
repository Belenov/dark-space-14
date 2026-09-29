using Robust.Shared.Configuration;

namespace Content.Server._DarkSpace.Lighting;

/// <summary>
/// Dark Space station lighting: dimmer lamps and random lamp faults.
/// </summary>
[CVarDefs]
public sealed class DSLightingCVars
{
    /// <summary>
    /// Multiplier for the energy (brightness) of every light bulb and tube when it spawns.
    /// </summary>
    public static readonly CVarDef<float> EnergyMultiplier =
        CVarDef.Create("darkspace.light_energy_mult", 0.6f, CVar.SERVERONLY);

    /// <summary>
    /// Multiplier for the radius of every light bulb and tube when it spawns.
    /// </summary>
    public static readonly CVarDef<float> RadiusMultiplier =
        CVarDef.Create("darkspace.light_radius_mult", 0.8f, CVar.SERVERONLY);

    /// <summary>
    /// Color the lamps are tinted towards (hex).
    /// </summary>
    public static readonly CVarDef<string> Tint =
        CVarDef.Create("darkspace.light_tint", "#FFC88A", CVar.SERVERONLY);

    /// <summary>
    /// How strongly the lamps are tinted, 0 = original color, 1 = pure tint.
    /// </summary>
    public static readonly CVarDef<float> TintStrength =
        CVarDef.Create("darkspace.light_tint_strength", 0.3f, CVar.SERVERONLY);

    /// <summary>
    /// Enables random lamp faults (flickering, dying out, brownouts).
    /// </summary>
    public static readonly CVarDef<bool> FaultsEnabled =
        CVarDef.Create("darkspace.light_faults", true, CVar.SERVERONLY);

    /// <summary>
    /// Chance that a lamp fixture is faulty from roundstart. Faulty lamps misbehave far more often.
    /// </summary>
    public static readonly CVarDef<float> FaultyChance =
        CVarDef.Create("darkspace.light_faulty_chance", 0.07f, CVar.SERVERONLY);

    /// <summary>
    /// Average seconds between two lamp faults on the whole server, before the per-round intensity roll.
    /// </summary>
    public static readonly CVarDef<float> FaultInterval =
        CVarDef.Create("darkspace.light_fault_interval", 6f, CVar.SERVERONLY);
}
