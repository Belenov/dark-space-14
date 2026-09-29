using Robust.Shared.Configuration;

namespace Content.Shared._DarkSpace.CCVar;

/// <summary>
/// Dark Space specific CVars.
/// </summary>
[CVarDefs]
public sealed class DSCCVars
{
    /// <summary>
    /// Height of the main game viewport in tiles. Lower values show less of the map with bigger sprites.
    /// Upstream hardcodes 15. Keep viewport.minimum_width/maximum_width in proportion (about 1.4x height).
    /// </summary>
    public static readonly CVarDef<int> ViewportHeight =
        CVarDef.Create("darkspace.viewport_height", 15, CVar.REPLICATED | CVar.SERVER);
}
