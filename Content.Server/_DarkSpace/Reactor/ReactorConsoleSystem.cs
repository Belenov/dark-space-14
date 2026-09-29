using Content.Shared._DarkSpace.Reactor;
using Content.Shared.Access.Systems;
using Content.Shared.Popups;
using Robust.Server.GameObjects;

namespace Content.Server._DarkSpace.Reactor;

public sealed partial class ReactorConsoleSystem : EntitySystem
{
    [Dependency] private UserInterfaceSystem _ui = default!;
    [Dependency] private AccessReaderSystem _access = default!;
    [Dependency] private SharedPopupSystem _popup = default!;
    [Dependency] private SharedTransformSystem _xform = default!;
    [Dependency] private AppearanceSystem _appearance = default!;
    [Dependency] private ReactorCoreSystem _core = default!;

    public override void Initialize()
    {
        base.Initialize();
        SubscribeLocalEvent<ReactorConsoleComponent, MapInitEvent>((uid, comp, _) => TryLink((uid, comp)));

        Subs.BuiEvents<ReactorConsoleComponent>(ReactorUiKey.Key, subs =>
        {
            subs.Event<BoundUIOpenedEvent>((ent, ref _) =>
            {
                TryLink(ent);
                UpdateUi(ent);
            });
            subs.Event<ReactorSetRodsMessage>((ent, ref args) =>
            {
                if (TryGetCore(ent, args.Actor, out var core))
                    _core.SetRodTarget(core, args.Target, args.Actor);
            });
            subs.Event<ReactorScramMessage>((ent, ref args) =>
            {
                if (TryGetCore(ent, args.Actor, out var core))
                    _core.Scram(core, args.Actor);
            });
            subs.Event<ReactorResetScramMessage>((ent, ref args) =>
            {
                if (TryGetCore(ent, args.Actor, out var core))
                    _core.ResetScram(core, args.Actor);
            });
        });
    }

    private bool TryGetCore(Entity<ReactorConsoleComponent> ent, EntityUid user, out Entity<ReactorCoreComponent> core)
    {
        core = default;
        if (!_access.IsAllowed(user, ent))
        {
            _popup.PopupEntity(Loc.GetString("ds-reactor-access-denied"), ent, user);
            return false;
        }

        if (ent.Comp.Core is not { } uid || !TryComp<ReactorCoreComponent>(uid, out var comp))
            return false;

        core = (uid, comp);
        return true;
    }

    /// <summary>
    /// Links the console to the closest core on its grid within range.
    /// </summary>
    public void TryLink(Entity<ReactorConsoleComponent> ent)
    {
        if (ent.Comp.Core is { } existing && Exists(existing))
            return;

        ent.Comp.Core = null;
        var xform = Transform(ent);
        var pos = _xform.GetWorldPosition(xform);
        var best = ent.Comp.Range * ent.Comp.Range;

        var query = EntityQueryEnumerator<ReactorCoreComponent, TransformComponent>();
        while (query.MoveNext(out var uid, out _, out var coreXform))
        {
            if (coreXform.GridUid != xform.GridUid)
                continue;

            var dist = (_xform.GetWorldPosition(coreXform) - pos).LengthSquared();
            if (dist > best)
                continue;

            best = dist;
            ent.Comp.Core = uid;
        }
    }

    public void UpdateLinkedConsoles(Entity<ReactorCoreComponent> core)
    {
        var state = _core.GetState(core.Comp);
        ReactorUiState? ui = null;

        var query = EntityQueryEnumerator<ReactorConsoleComponent>();
        while (query.MoveNext(out var uid, out var console))
        {
            if (console.Core != core.Owner)
                continue;

            _appearance.SetData(uid, ReactorConsoleVisuals.State, state);
            if (!_ui.IsUiOpen(uid, ReactorUiKey.Key))
                continue;

            ui ??= _core.BuildUiState(core.Comp);
            _ui.SetUiState(uid, ReactorUiKey.Key, ui);
        }
    }

    private void UpdateUi(Entity<ReactorConsoleComponent> ent)
    {
        if (ent.Comp.Core is { } uid && TryComp<ReactorCoreComponent>(uid, out var core))
        {
            _ui.SetUiState(ent.Owner, ReactorUiKey.Key, _core.BuildUiState(core));
            return;
        }

        _ui.SetUiState(ent.Owner, ReactorUiKey.Key, new ReactorUiState(0, 1, 0, 0, null, 0, 0, 0, 0, 0,
            false, false, 0, 0, 0, 0, new List<ReactorCellType>(), new List<float>(), false));
    }
}
