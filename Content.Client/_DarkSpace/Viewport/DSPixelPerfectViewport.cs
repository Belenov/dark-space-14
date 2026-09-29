using Content.Client.UserInterface.Systems.Viewport;
using Content.Client.Viewport;
using Content.Shared._DarkSpace.CCVar;
using Content.Shared.CCVar;
using Robust.Client.Graphics;
using Robust.Shared.Configuration;

namespace Content.Client._DarkSpace.Viewport;

/// <summary>
/// Closer camera that keeps pixel art crisp: instead of zooming the eye by a fractional amount,
/// the game view is drawn at a whole-number scale (every sprite pixel becomes exactly 2x2, 3x3, 4x4... screen pixels)
/// and the viewport shows as many tiles as fit the screen at that scale, close to <see cref="DSCCVars.ViewTiles"/>.
/// </summary>
public static class DSPixelPerfectViewport
{
    /// <summary>
    /// Configures <paramref name="viewport"/> for a control of <paramref name="controlSize"/> pixels.
    /// Returns false when the mode is off, so the caller falls back to the upstream scaling.
    /// </summary>
    public static bool TryApply(ScalingViewport viewport, Vector2i controlSize, IConfigurationManager cfg)
    {
        var targetTiles = cfg.GetCVar(DSCCVars.ViewTiles);
        if (targetTiles <= 0 || controlSize.X <= 0 || controlSize.Y <= 0)
            return false;

        // Screen pixels per sprite pixel, picked so the view height lands closest to the target tile count.
        var scale = Math.Max(1, (int) MathF.Round(controlSize.Y / (float) (EyeManager.PixelsPerMeter * targetTiles),
            MidpointRounding.AwayFromZero));

        // Viewport size in unscaled pixels: fill the control, at most the upstream widest aspect (21x15).
        var height = (controlSize.Y + scale - 1) / scale;
        var maxAspect = cfg.GetCVar(CCVars.ViewportMaximumWidth) / (float) ViewportUIController.ViewportHeight;
        var width = Math.Min((controlSize.X + scale - 1) / scale, (int) MathF.Ceiling(height * maxAspect));
        var size = new Vector2i(width, height);

        // Setters recreate the render target, so only touch what changed.
        if (viewport.ViewportSize != size)
            viewport.ViewportSize = size;
        if (viewport.StretchMode != ScalingViewportStretchMode.Nearest)
            viewport.StretchMode = ScalingViewportStretchMode.Nearest;
        if (viewport.RenderScaleMode != ScalingViewportRenderScaleMode.Fixed)
            viewport.RenderScaleMode = ScalingViewportRenderScaleMode.Fixed;

        // "Low-res" option renders at 1x and lets the whole-number stretch do the upscaling.
        var renderScale = cfg.GetCVar(CCVars.ViewportScaleRender) ? scale : 1;
        if (viewport.FixedRenderScale != renderScale)
            viewport.FixedRenderScale = renderScale;

        // Drawn at exactly size * scale, centered; overshoot of under one sprite pixel is clipped.
        viewport.FixedStretchSize = size * scale;
        return true;
    }
}
