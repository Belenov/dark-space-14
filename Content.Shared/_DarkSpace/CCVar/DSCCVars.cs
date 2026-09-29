using Robust.Shared.Configuration;

namespace Content.Shared._DarkSpace.CCVar;

/// <summary>
/// Dark Space specific CVars.
/// </summary>
[CVarDefs]
public sealed class DSCCVars
{
    /// <summary>
    /// Camera zoom applied to a player's entity when they attach to it. Below 1 is closer (1 = upstream default).
    /// The same zoom is used on every monitor, since the visible tile count does not depend on screen size.
    /// Fractional zooms stretch sprite pixels unevenly; prefer <see cref="ViewTiles"/> for a crisp closer view.
    /// </summary>
    public static readonly CVarDef<float> DefaultZoom =
        CVarDef.Create("darkspace.default_zoom", 1f, CVar.SERVER | CVar.ARCHIVE);

    /// <summary>
    /// Pixel-perfect closer camera: roughly how many tiles tall the game view is (upstream shows 15).
    /// The view is drawn at a whole-number scale, so the exact count varies a little by screen height.
    /// 0 keeps upstream viewport scaling.
    /// </summary>
    public static readonly CVarDef<int> ViewTiles =
        CVarDef.Create("darkspace.view_tiles", 0, CVar.SERVER | CVar.REPLICATED | CVar.ARCHIVE);
}
