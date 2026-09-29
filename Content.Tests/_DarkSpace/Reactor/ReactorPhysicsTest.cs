using Content.Shared._DarkSpace.Reactor;
using System.Collections.Generic;
using Content.Server._DarkSpace.Reactor;
using NUnit.Framework;

namespace Content.Tests._DarkSpace.Reactor;

[TestFixture]
[TestOf(typeof(ReactorPhysics))]
public sealed class ReactorPhysicsTest
{
    private static readonly List<string> Checkerboard = new() { "GFGFGFG", "FRFRFRF", "GFGFGFG", "FRFRFRF", "GFGFGFG", "FRFRFRF", "GFGFGFG" };

    private static float K(float rods, List<string> layout = null)
    {
        var cells = ReactorCoreSystem.ParseLayout(layout ?? Checkerboard, 7);
        return ReactorPhysics.LayoutK(cells, 7, rods, 1f, new ReactorCoefficients());
    }

    [Test]
    public void DefaultLayoutIsControllable()
    {
        Assert.That(K(0f), Is.GreaterThan(1f), "withdrawn rods must make the core supercritical");
        Assert.That(K(1f), Is.LessThan(0.9f), "inserted rods must shut the core down");
        Assert.That(K(0.43f), Is.InRange(0.99f, 1.01f), "default hall should go critical around 43% rods");
    }

    [Test]
    public void RodsReduceReactivityMonotonically()
    {
        Assert.That(K(0.3f), Is.GreaterThan(K(0.6f)));
    }

    [Test]
    public void GraphiteModeratesAndEmptyCoreIsDead()
    {
        var withGraphite = K(0.5f);
        var withoutGraphite = K(0.5f, new() { ".F.F.F.", "FRFRFRF", ".F.F.F.", "FRFRFRF", ".F.F.F.", "FRFRFRF", ".F.F.F." });
        Assert.That(withGraphite, Is.GreaterThan(withoutGraphite));
        Assert.That(K(0f, new() { "GGGGG" }), Is.Zero);
    }

    [Test]
    public void LosingCoolantAddsReactivity()
    {
        var c = new ReactorCoefficients();
        Assert.That(ReactorPhysics.ThermalFeedback(600f, null, c), Is.GreaterThan(ReactorPhysics.ThermalFeedback(600f, 300f, c)));
        Assert.That(ReactorPhysics.ThermalFeedback(1500f, 300f, c), Is.LessThan(ReactorPhysics.ThermalFeedback(600f, 300f, c)));
    }

    [Test]
    public void PowerGrowsWhenSupercriticalAndIsClamped()
    {
        Assert.That(ReactorPhysics.StepPower(1000f, 1.05f, 4f, 1f, 0f, 1e7f), Is.GreaterThan(1000f));
        Assert.That(ReactorPhysics.StepPower(1000f, 0.95f, 4f, 1f, 0f, 1e7f), Is.LessThan(1000f));
        Assert.That(ReactorPhysics.StepPower(1e7f, 2f, 4f, 10f, 0f, 1e7f), Is.EqualTo(1e7f));
    }

    [Test]
    public void HeatTransferDoesNotOvershoot()
    {
        var q = ReactorPhysics.HeatToCoolant(1000f, 300f, 1e9f, 500_000f, 1_000f, 1f);
        var coolantAfter = 300f + q / 1_000f;
        var coreAfter = 1000f - q / 500_000f;
        Assert.That(coolantAfter, Is.LessThanOrEqualTo(coreAfter + 0.01f));
    }
}
