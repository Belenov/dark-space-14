using Robust.Shared.GameStates;
using Robust.Shared.Serialization;

namespace Content.Shared._DarkSpace.Reactor;

/// <summary>
/// An assembly that goes into a reactor channel: fuel (ТВС), control rod or graphite block.
/// </summary>
[RegisterComponent, NetworkedComponent]
public sealed partial class ReactorAssemblyComponent : Component
{
    [DataField(required: true)]
    public ReactorCellType CellType;
}

/// <summary>
/// One channel in the reactor lid. The core entity reads the assembly in each channel around it.
/// </summary>
[RegisterComponent, NetworkedComponent]
public sealed partial class ReactorChannelComponent : Component
{
    [DataField]
    public string SlotId = "assembly";
}

[Serializable, NetSerializable]
public enum ReactorChannelVisuals : byte
{
    /// <summary><see cref="ReactorCellType"/> in the channel.</summary>
    Contents,

    /// <summary>Neutron flux in the channel, 0 (dark) to 4 (white hot).</summary>
    Flux,
}

[Serializable, NetSerializable]
public enum ReactorCoreVisuals : byte
{
    /// <summary><see cref="ReactorCoreState"/>.</summary>
    State,

    /// <summary>Crack overlay level 0..3 from core integrity.</summary>
    Cracks,

    /// <summary>AZ-5 beacons flashing.</summary>
    Scram,
}

[Serializable, NetSerializable]
public enum ReactorCoreState : byte
{
    Off,
    Low,
    Nominal,
    Hot,
    Critical,
    Wrecked,
}

[Serializable, NetSerializable]
public enum ReactorConsoleVisuals : byte
{
    /// <summary><see cref="ReactorCoreState"/> of the linked core, or Off when unlinked.</summary>
    State,
}
