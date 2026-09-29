namespace Content.Server._DarkSpace.Reactor;

/// <summary>
/// Control rod console (пульт СУЗ). Links to the nearest reactor core on the same grid.
/// </summary>
[RegisterComponent, Access(typeof(ReactorConsoleSystem))]
public sealed partial class ReactorConsoleComponent : Component
{
    [ViewVariables]
    public EntityUid? Core;

    /// <summary>How far, in tiles, the console looks for a core.</summary>
    [DataField]
    public float Range = 30f;
}
