using Robust.Shared.GameStates;

namespace Content.Shared._DarkSpace.Weapons;

/// <summary>
/// Scales this gun's camera kick and spread by the holder's <see cref="FirearmsSkillComponent"/>,
/// and shoves the shooter back on every shot.
/// Multiplier is lerped from <see cref="UnskilledMultiplier"/> (skill 0) to <see cref="SkilledMultiplier"/> (skill 1).
/// </summary>
[RegisterComponent, NetworkedComponent, AutoGenerateComponentState]
[Access(typeof(SkillScaledRecoilSystem))]
public sealed partial class SkillScaledRecoilComponent : Component
{
    [DataField, AutoNetworkedField]
    public float UnskilledMultiplier = 1.6f;

    [DataField, AutoNetworkedField]
    public float SkilledMultiplier = 0.4f;

    /// <summary>
    /// Impulse applied to the shooter against the shot direction, before the skill multiplier.
    /// </summary>
    [DataField, AutoNetworkedField]
    public float PushImpulse = 20f;
}
