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
    /// </summary>
    public static readonly CVarDef<float> DefaultZoom =
        CVarDef.Create("darkspace.default_zoom", 1f, CVar.SERVER | CVar.ARCHIVE);

    /// <summary>
    /// Whether windows that open by themselves on join (rules popup, new-player guidebook) are shown.
    /// </summary>
    public static readonly CVarDef<bool> JoinPopups =
        CVarDef.Create("darkspace.join_popups", false, CVar.SERVER | CVar.REPLICATED | CVar.ARCHIVE);
}
