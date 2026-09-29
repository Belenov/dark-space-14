using Content.Shared._DarkSpace.Reactor;

namespace Content.Server._DarkSpace.Reactor;

/// <summary>
/// Tunable coefficients of the core. Kept separate from the component so the math can be unit tested.
/// </summary>
[DataDefinition]
public sealed partial class ReactorCoefficients
{
    /// <summary>Bonus to a fuel cell per adjacent graphite moderator.</summary>
    [DataField] public float Graphite = 0.10f;

    /// <summary>Bonus to a fuel cell per adjacent fuel cell.</summary>
    [DataField] public float Fuel = 0.04f;

    /// <summary>Penalty to a fuel cell per adjacent control rod at full insertion.</summary>
    [DataField] public float Rod = 0.18f;

    /// <summary>Penalty to a fuel cell per side facing the edge of the core (neutron leakage).</summary>
    [DataField] public float Edge = 0.06f;

    /// <summary>k_eff change per fuel cell above <see cref="ReferenceFuelCount"/>.</summary>
    [DataField] public float FuelMass = 0.015f;

    [DataField] public int ReferenceFuelCount = 24;

    /// <summary>Overall leakage multiplier applied to the averaged core.</summary>
    [DataField] public float Base = 0.95f;

    /// <summary>Negative fuel-temperature (Doppler) feedback per 1000 K above 300 K.</summary>
    [DataField] public float Doppler = 0.03f;

    /// <summary>Positive coolant void feedback per 1000 K of coolant above <see cref="VoidThreshold"/>.</summary>
    [DataField] public float Void = 0.05f;

    [DataField] public float VoidThreshold = 400f;

    /// <summary>Reactivity added by losing coolant entirely.</summary>
    [DataField] public float NoCoolant = 0.05f;
}

public static class ReactorPhysics
{
    /// <summary>
    /// Local multiplication of every channel: 0 for non-fuel, otherwise 1 plus the effect of its four neighbours.
    /// </summary>
    public static float[] CellFactors(IReadOnlyList<ReactorCellType> cells, int size, float rodInsertion, ReactorCoefficients c)
    {
        var factors = new float[cells.Count];
        for (var y = 0; y < size; y++)
        {
            for (var x = 0; x < size; x++)
            {
                if (cells[y * size + x] != ReactorCellType.Fuel)
                    continue;

                factors[y * size + x] = MathF.Max(0f, 1f
                    + Neighbour(cells, size, x - 1, y, rodInsertion, c)
                    + Neighbour(cells, size, x + 1, y, rodInsertion, c)
                    + Neighbour(cells, size, x, y - 1, rodInsertion, c)
                    + Neighbour(cells, size, x, y + 1, rodInsertion, c));
            }
        }

        return factors;
    }

    /// <summary>
    /// Static multiplication factor of a core layout, before temperature feedback.
    /// Each fuel cell is weighted by its four neighbours, so the layout itself is the puzzle.
    /// </summary>
    public static float LayoutK(IReadOnlyList<ReactorCellType> cells, int size, float rodInsertion, float reproduction, ReactorCoefficients c)
    {
        return LayoutK(cells, CellFactors(cells, size, rodInsertion, c), reproduction, c);
    }

    public static float LayoutK(IReadOnlyList<ReactorCellType> cells, float[] factors, float reproduction, ReactorCoefficients c)
    {
        var fuelCount = 0;
        var sum = 0f;
        for (var i = 0; i < cells.Count; i++)
        {
            if (cells[i] != ReactorCellType.Fuel)
                continue;

            fuelCount++;
            sum += factors[i];
        }

        if (fuelCount == 0)
            return 0f;

        var mass = 1f + c.FuelMass * (fuelCount - c.ReferenceFuelCount);
        return MathF.Max(0f, sum / fuelCount * mass * c.Base * reproduction);
    }

    private static float Neighbour(IReadOnlyList<ReactorCellType> cells, int size, int x, int y, float rodInsertion, ReactorCoefficients c)
    {
        if (x < 0 || y < 0 || x >= size || y >= size)
            return -c.Edge;

        return cells[y * size + x] switch
        {
            ReactorCellType.Graphite => c.Graphite,
            ReactorCellType.Fuel => c.Fuel,
            ReactorCellType.Rod => -c.Rod * rodInsertion,
            _ => 0f,
        };
    }

    /// <summary>
    /// Temperature feedback: hot fuel damps the reaction, hot or missing coolant speeds it up (positive void coefficient).
    /// </summary>
    public static float ThermalFeedback(float coreTemp, float? coolantTemp, ReactorCoefficients c)
    {
        var feedback = -c.Doppler * MathF.Max(0f, coreTemp - 300f) / 1000f;

        if (coolantTemp is not { } gas)
            return feedback + c.NoCoolant;

        return feedback + c.Void * MathF.Max(0f, gas - c.VoidThreshold) / 1000f;
    }

    /// <summary>
    /// Point-kinetics step: power grows or decays exponentially with (k - 1) over the generation time.
    /// </summary>
    public static float StepPower(float power, float k, float generationTime, float dt, float sourcePower, float maxPower)
    {
        var next = power * MathF.Exp((k - 1f) * dt / generationTime);
        return Math.Clamp(MathF.Max(next, sourcePower), 0f, maxPower);
    }

    /// <summary>
    /// Heat moved from core to coolant this step, capped so the two never overshoot equilibrium.
    /// </summary>
    public static float HeatToCoolant(float coreTemp, float coolantTemp, float conductance, float coreHeatCapacity, float coolantHeatCapacity, float dt)
    {
        var dT = coreTemp - coolantTemp;
        var q = conductance * dT * dt;

        if (coolantHeatCapacity <= 0f)
            return 0f;

        var limit = dT * coreHeatCapacity * coolantHeatCapacity / (coreHeatCapacity + coolantHeatCapacity);
        return MathF.Abs(q) > MathF.Abs(limit) ? limit : q;
    }
}
