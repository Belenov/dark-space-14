using Robust.Shared.GameStates;

namespace Content.Shared._DarkSpace.Weapons;

/// <summary>
/// Placeholder for a future skills system: how well this mob handles firearms.
/// 0 = never held a gun, 1 = expert. Mobs without this component use <see cref="DefaultSkill"/>.
/// Guns with <see cref="SkillScaledRecoilComponent"/> kick and spread less the higher it is.
/// </summary>
[RegisterComponent, NetworkedComponent, AutoGenerateComponentState]
[Access(typeof(SkillScaledRecoilSystem))]
public sealed partial class FirearmsSkillComponent : Component
{
    public const float DefaultSkill = 0.5f;

    [DataField, AutoNetworkedField]
    public float Skill = DefaultSkill;
}
