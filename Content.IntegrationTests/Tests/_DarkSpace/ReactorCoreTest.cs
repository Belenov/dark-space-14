using Content.IntegrationTests.Fixtures;
using Content.Server._DarkSpace.Reactor;
using Robust.Shared.GameObjects;

namespace Content.IntegrationTests.Tests._DarkSpace;

[TestFixture]
public sealed class ReactorCoreTest : GameTest
{
    [Test]
    public async Task ReactorSpawnsWithLayoutAndPassport()
    {
        var pair = Pair;
        var server = pair.Server;
        var testMap = await pair.CreateTestMap();
        var entMan = server.ResolveDependency<IEntityManager>();

        await server.WaitAssertion(() =>
        {
            var uid = entMan.SpawnEntity("DarkSpaceReactorCore", testMap.GridCoords);
            var comp = entMan.GetComponent<ReactorCoreComponent>(uid);

            Assert.That(comp.Cells, Has.Count.EqualTo(25));
            Assert.That(comp.Reproduction, Is.InRange(comp.ReproductionMin, comp.ReproductionMax));
            Assert.That(comp.BatchNumber, Is.InRange(1000, 9999));
        });

        await pair.RunTicksSync(30);

        await server.WaitAssertion(() =>
        {
            var query = entMan.EntityQueryEnumerator<ReactorCoreComponent>();
            Assert.That(query.MoveNext(out _, out var comp));
            Assert.That(comp.Melted, Is.False);
        });
    }
}
