using Robust.Shared.Serialization;

namespace Content.Shared._DarkSpace.Reactor;

/// <summary>
/// What sits in one channel of the reactor core.
/// </summary>
[Serializable, NetSerializable]
public enum ReactorCellType : byte
{
    Empty,
    Fuel,
    Rod,
    Graphite,
}

[Serializable, NetSerializable]
public enum ReactorUiKey : byte
{
    Key,
}

[Serializable, NetSerializable]
public sealed class ReactorUiState(
    float power,
    float nominalPower,
    float keff,
    float coreTemperature,
    float? coolantTemperature,
    float warningTemperature,
    float meltdownTemperature,
    float rodInsertion,
    float targetRodInsertion,
    float integrity,
    bool scrammed,
    bool melted,
    int batchNumber,
    float passportReproduction,
    float passportError,
    int size,
    List<ReactorCellType> cells,
    List<float> flux,
    bool linked) : BoundUserInterfaceState
{
    public readonly float Power = power;
    public readonly float NominalPower = nominalPower;
    public readonly float KEff = keff;
    public readonly float CoreTemperature = coreTemperature;
    public readonly float? CoolantTemperature = coolantTemperature;
    public readonly float WarningTemperature = warningTemperature;
    public readonly float MeltdownTemperature = meltdownTemperature;
    public readonly float RodInsertion = rodInsertion;
    public readonly float TargetRodInsertion = targetRodInsertion;
    public readonly float Integrity = integrity;
    public readonly bool Scrammed = scrammed;
    public readonly bool Melted = melted;
    public readonly int BatchNumber = batchNumber;
    public readonly float PassportReproduction = passportReproduction;
    public readonly float PassportError = passportError;
    public readonly int Size = size;
    public readonly List<ReactorCellType> Cells = cells;

    /// <summary>Thermal power per channel, watts.</summary>
    public readonly List<float> Flux = flux;

    /// <summary>False when the console has no reactor in range.</summary>
    public readonly bool Linked = linked;
}

/// <summary>Set the rod target insertion, 0..1.</summary>
[Serializable, NetSerializable]
public sealed class ReactorSetRodsMessage(float target) : BoundUserInterfaceMessage
{
    public readonly float Target = target;
}

[Serializable, NetSerializable]
public sealed class ReactorScramMessage : BoundUserInterfaceMessage;

[Serializable, NetSerializable]
public sealed class ReactorResetScramMessage : BoundUserInterfaceMessage;
