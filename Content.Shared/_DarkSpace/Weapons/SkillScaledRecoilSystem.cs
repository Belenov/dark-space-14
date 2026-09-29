using Content.Shared.Hands;
using Content.Shared.Hands.Components;
using Content.Shared.Hands.EntitySystems;
using Content.Shared.Weapons.Ranged.Components;
using Content.Shared.Weapons.Ranged.Events;
using Content.Shared.Weapons.Ranged.Systems;
using Robust.Shared.Containers;
using Robust.Shared.Physics.Components;
using Robust.Shared.Physics.Systems;

namespace Content.Shared._DarkSpace.Weapons;

/// <summary>
/// Makes recoil (camera kick, spread growth and a shove) depend on the shooter's firearms skill.
/// </summary>
public sealed partial class SkillScaledRecoilSystem : EntitySystem
{
    [Dependency] private SharedGunSystem _gun = default!;
    [Dependency] private SharedHandsSystem _hands = default!;
    [Dependency] private SharedContainerSystem _container = default!;
    [Dependency] private SharedPhysicsSystem _physics = default!;
    [Dependency] private SharedTransformSystem _transform = default!;

    public override void Initialize()
    {
        base.Initialize();

        SubscribeLocalEvent<SkillScaledRecoilComponent, GunRefreshModifiersEvent>(OnRefreshModifiers);
        SubscribeLocalEvent<SkillScaledRecoilComponent, GotEquippedHandEvent>(OnEquipped);
        SubscribeLocalEvent<SkillScaledRecoilComponent, GotUnequippedHandEvent>(OnUnequipped);
        SubscribeLocalEvent<SkillScaledRecoilComponent, GunShotEvent>(OnGunShot);
    }

    /// <summary>
    /// Entry point for a future skills system.
    /// </summary>
    public void SetSkill(EntityUid uid, float skill)
    {
        var comp = EnsureComp<FirearmsSkillComponent>(uid);
        comp.Skill = Math.Clamp(skill, 0f, 1f);
        Dirty(uid, comp);

        foreach (var held in _hands.EnumerateHeld(uid))
        {
            if (HasComp<SkillScaledRecoilComponent>(held))
                _gun.RefreshModifiers(held);
        }
    }

    public float GetSkill(EntityUid? uid)
    {
        return CompOrNull<FirearmsSkillComponent>(uid)?.Skill ?? FirearmsSkillComponent.DefaultSkill;
    }

    private float GetMultiplier(SkillScaledRecoilComponent comp, EntityUid? holder)
    {
        return MathHelper.Lerp(comp.UnskilledMultiplier, comp.SkilledMultiplier, GetSkill(holder));
    }

    private EntityUid? GetHolder(EntityUid gun)
    {
        if (!_container.TryGetContainingContainer((gun, null, null), out var container))
            return null;

        var owner = container.Owner;
        return HasComp<HandsComponent>(owner) && _hands.IsHolding(owner, gun) ? owner : null;
    }

    private void OnRefreshModifiers(Entity<SkillScaledRecoilComponent> ent, ref GunRefreshModifiersEvent args)
    {
        var mult = GetMultiplier(ent.Comp, GetHolder(ent));
        args.CameraRecoilScalar *= mult;
        args.AngleIncrease *= mult;
        args.MaxAngle *= mult;
    }

    private void OnEquipped(Entity<SkillScaledRecoilComponent> ent, ref GotEquippedHandEvent args)
    {
        _gun.RefreshModifiers(ent.Owner);
    }

    private void OnUnequipped(Entity<SkillScaledRecoilComponent> ent, ref GotUnequippedHandEvent args)
    {
        _gun.RefreshModifiers(ent.Owner);
    }

    private void OnGunShot(Entity<SkillScaledRecoilComponent> ent, ref GunShotEvent args)
    {
        if (ent.Comp.PushImpulse <= 0f ||
            !TryComp<GunComponent>(ent, out var gun) ||
            gun.ShootCoordinates is not { } target ||
            !TryComp<PhysicsComponent>(args.User, out var physics))
        {
            return;
        }

        var from = _transform.GetMapCoordinates(args.User).Position;
        var to = _transform.ToMapCoordinates(target).Position;
        var dir = to - from;
        if (dir.LengthSquared() < 0.0001f)
            return;

        var impulse = ent.Comp.PushImpulse * GetMultiplier(ent.Comp, args.User);
        _physics.ApplyLinearImpulse(args.User, -dir.Normalized() * impulse, body: physics);
    }
}
