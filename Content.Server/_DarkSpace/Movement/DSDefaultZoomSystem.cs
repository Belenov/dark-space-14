using System.Numerics;
using Content.Shared._DarkSpace.CCVar;
using Content.Shared.Movement.Components;
using Content.Shared.Movement.Systems;
using Robust.Shared.Configuration;
using Robust.Shared.Player;

namespace Content.Server._DarkSpace.Movement;

/// <summary>
/// Zooms the camera in to <see cref="DSCCVars.DefaultZoom"/> when a player takes control of an entity.
/// Players can still zoom with the usual zoom keys; the reset key returns to upstream zoom 1.
/// </summary>
public sealed partial class DSDefaultZoomSystem : EntitySystem
{
    [Dependency] private IConfigurationManager _cfg = default!;
    [Dependency] private SharedContentEyeSystem _contentEye = default!;

    public override void Initialize()
    {
        base.Initialize();
        SubscribeLocalEvent<PlayerAttachedEvent>(OnPlayerAttached);
    }

    private void OnPlayerAttached(PlayerAttachedEvent args)
    {
        if (!TryComp<ContentEyeComponent>(args.Entity, out var eye))
            return;

        // Only replace the untouched default, so entities with a custom zoom keep it.
        if (eye.TargetZoom != SharedContentEyeSystem.DefaultZoom)
            return;

        var zoom = _cfg.GetCVar(DSCCVars.DefaultZoom);
        _contentEye.SetZoom(args.Entity, new Vector2(zoom), eye: eye);
    }
}
