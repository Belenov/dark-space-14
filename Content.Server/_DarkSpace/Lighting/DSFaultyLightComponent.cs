namespace Content.Server._DarkSpace.Lighting;

/// <summary>
/// A lamp fixture with bad wiring or a dying starter. It is picked for faults much more often than a healthy lamp.
/// </summary>
[RegisterComponent]
public sealed partial class DSFaultyLightComponent : Component
{
    /// <summary>
    /// 0..1, how badly this lamp is broken. Higher means more frequent and nastier faults.
    /// </summary>
    [DataField]
    public float Severity = 0.5f;
}

/// <summary>
/// A fault currently happening to this lamp; undone when <see cref="EndTime"/> passes.
/// </summary>
[RegisterComponent]
public sealed partial class DSLightFaultComponent : Component
{
    [DataField]
    public DSLightFault Fault;

    [DataField]
    public TimeSpan EndTime;

    /// <summary>
    /// For brownouts: the energy the lamp had before it was dimmed.
    /// </summary>
    [DataField]
    public float OriginalEnergy;

    /// <summary>
    /// For brownouts: the energy we dimmed it to, to tell if something else changed the light since.
    /// </summary>
    [DataField]
    public float DimmedEnergy;
}

public enum DSLightFault : byte
{
    /// <summary>A short stutter of a second or three.</summary>
    Stutter,
    /// <summary>A long, annoying flicker.</summary>
    Flicker,
    /// <summary>The lamp goes dark for a while, then clicks back on.</summary>
    DieOut,
    /// <summary>The lamp sags to a dim glow for a while.</summary>
    Brownout,
}
