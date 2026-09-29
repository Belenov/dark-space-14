using Content.Shared._DarkSpace.Reactor;
using Robust.Shared.Prototypes;

namespace Content.Server._DarkSpace.Reactor;

/// <summary>
/// Isotope reactor core ("ИР-7 Заря"). Does not produce electricity itself:
/// it heats the gas in its pipe, and the TEG on that loop turns the heat into power.
/// </summary>
[RegisterComponent, Access(typeof(ReactorCoreSystem))]
public sealed partial class ReactorCoreComponent : Component
{
    [DataField]
    public string PipeName = "pipe";

    /// <summary>
    /// Side length of the square channel grid. The core entity sits on the centre tile,
    /// channels are read from the tiles around it.
    /// </summary>
    [DataField]
    public int Size = 7;

    /// <summary>
    /// If set, on map init the core spawns any missing channels around itself and fills them per this layout,
    /// one string per row: F = fuel, R = control rod, G = graphite, . = empty channel.
    /// Mapped cores with their own channels are left untouched.
    /// </summary>
    [DataField]
    public List<string> Layout = new();

    [DataField]
    public EntProtoId ChannelPrototype = "DarkSpaceReactorChannel";

    [DataField]
    public Dictionary<ReactorCellType, EntProtoId> AssemblyPrototypes = new()
    {
        [ReactorCellType.Fuel] = "DarkSpaceReactorFuelU235",
        [ReactorCellType.Rod] = "DarkSpaceReactorControlRod",
        [ReactorCellType.Graphite] = "DarkSpaceReactorGraphite",
    };

    /// <summary>Contents of each channel, row by row, refreshed every tick.</summary>
    [ViewVariables]
    public List<ReactorCellType> Cells = new();

    /// <summary>Channel entity per cell, null where the channel is missing.</summary>
    [ViewVariables]
    public List<EntityUid?> Channels = new();

    /// <summary>Thermal power per channel, watts.</summary>
    [ViewVariables]
    public List<float> Flux = new();

    [DataField]
    public ReactorCoefficients Coefficients = new();

    #region Fuel batch passport

    /// <summary>Real reproduction factor of this round's fuel batch, rolled on map init.</summary>
    [ViewVariables(VVAccess.ReadWrite)]
    public float Reproduction = 1f;

    /// <summary>What the passport claims. Differs from the real value by up to <see cref="PassportError"/>.</summary>
    [ViewVariables]
    public float PassportReproduction = 1f;

    [ViewVariables]
    public int BatchNumber;

    [DataField]
    public float ReproductionMin = 0.94f;

    [DataField]
    public float ReproductionMax = 1.06f;

    [DataField]
    public float PassportError = 0.08f;

    #endregion

    #region Control rods

    /// <summary>Current rod insertion, 0 = fully withdrawn, 1 = fully inserted.</summary>
    [DataField]
    public float RodInsertion = 1f;

    [DataField]
    public float TargetRodInsertion = 1f;

    /// <summary>Rod travel per second.</summary>
    [DataField]
    public float RodSpeed = 0.05f;

    [DataField]
    public float ScramRodSpeed = 0.12f;

    [DataField]
    public float RodStep = 0.05f;

    [ViewVariables]
    public bool Scrammed;

    /// <summary>Graphite displacers add reactivity for the first seconds after AZ-5.</summary>
    [DataField]
    public float ScramSpike = 0.04f;

    [DataField]
    public TimeSpan ScramSpikeDuration = TimeSpan.FromSeconds(4);

    [ViewVariables]
    public TimeSpan ScramSpikeEnd;

    [ViewVariables]
    public float ScramSpikeMagnitude;

    #endregion

    #region Kinetics and heat

    /// <summary>Thermal power, watts.</summary>
    [ViewVariables]
    public float Power;

    [ViewVariables]
    public float KEff;

    [DataField]
    public float NominalPower = 1_500_000f;

    [DataField]
    public float MaxPower = 20_000_000f;

    /// <summary>Background neutron source keeping a loaded core from going fully dark.</summary>
    [DataField]
    public float SourcePower = 1_000f;

    /// <summary>Seconds per e-fold at k = 2. Longer is gentler.</summary>
    [DataField]
    public float GenerationTime = 4f;

    [ViewVariables(VVAccess.ReadWrite)]
    public float CoreTemperature = 293.15f;

    [ViewVariables]
    public float? CoolantTemperature;

    [DataField]
    public float CoreHeatCapacity = 500_000f;

    /// <summary>Core-to-coolant heat transfer, W/K.</summary>
    [DataField]
    public float Conductance = 5_000f;

    #endregion

    #region Failure

    [DataField]
    public float WarningTemperature = 1200f;

    [DataField]
    public float MeltdownTemperature = 1800f;

    /// <summary>0..100. Drains while the core is above <see cref="MeltdownTemperature"/>.</summary>
    [ViewVariables(VVAccess.ReadWrite)]
    public float Integrity = 100f;

    [DataField]
    public float IntegrityLossRate = 1f;

    [ViewVariables]
    public bool WarningActive;

    [ViewVariables]
    public bool Melted;

    [DataField]
    public string CoriumPrototype = "DarkSpaceReactorCorium";

    [DataField]
    public float MeltdownExplosionIntensity = 400f;

    #endregion

    /// <summary>Radiation at the core per nominal power.</summary>
    [DataField]
    public float RadiationPerNominal = 3f;

    [DataField]
    public float BaseRadiation = 0.2f;
}
