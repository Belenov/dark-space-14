using System.Linq;
using Content.IntegrationTests.Fixtures;
using Content.Server._DarkSpace.Reactor;
using Content.Shared._DarkSpace.Reactor;
using Robust.Shared.GameObjects;
using Robust.Shared.Map;
using Robust.Shared.Maths;

namespace Content.IntegrationTests.Tests._DarkSpace;

[TestFixture]
public sealed class ReactorCoreTest : GameTest
{
    [Test]
    public async Task HallSpawnsChannelsAndConsoleLinks()
    {
        var pair = Pair;
        var server = pair.Server;
        var testMap = await pair.CreateTestMap();
        var entMan = server.ResolveDependency<IEntityManager>();
        var mapSys = server.System<SharedMapSystem>();

        EntityUid core = default;
        await server.WaitAssertion(() =>
        {
            // Make room for the 7x7 lid and a console.
            for (var x = -4; x <= 4; x++)
            for (var y = -4; y <= 4; y++)
                mapSys.SetTile(testMap.Grid, new Vector2i(x, y), testMap.Tile.Tile);

            core = entMan.SpawnEntity("DarkSpaceReactorCore", mapSys.GridTileToLocal(testMap.Grid, testMap.Grid, Vector2i.Zero));
            entMan.SpawnEntity("DarkSpaceReactorConsole", mapSys.GridTileToLocal(testMap.Grid, testMap.Grid, new Vector2i(4, 4)));
        });

        await pair.RunTicksSync(30);

        await server.WaitAssertion(() =>
        {
            var comp = entMan.GetComponent<ReactorCoreComponent>(core);
            Assert.That(comp.Channels.Count(c => c != null), Is.EqualTo(49));
            Assert.That(comp.Cells.Count(c => c == ReactorCellType.Fuel), Is.EqualTo(24));
            Assert.That(comp.Cells.Count(c => c == ReactorCellType.Rod), Is.EqualTo(9));
            Assert.That(comp.Reproduction, Is.InRange(comp.ReproductionMin, comp.ReproductionMax));
            Assert.That(comp.Melted, Is.False);

            var consoles = entMan.EntityQueryEnumerator<ReactorConsoleComponent>();
            Assert.That(consoles.MoveNext(out var console));
            Assert.That(console.Core, Is.EqualTo(core));
        });
    }
}
