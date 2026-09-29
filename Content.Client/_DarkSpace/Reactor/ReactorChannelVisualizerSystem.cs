using Content.Shared._DarkSpace.Reactor;
using Robust.Client.GameObjects;

namespace Content.Client._DarkSpace.Reactor;

/// <summary>
/// Picks the channel cap sprite from its contents, switching to the "-hot" variant under high flux.
/// </summary>
public sealed partial class ReactorChannelVisualizerSystem : VisualizerSystem<ReactorChannelComponent>
{
    /// <summary>Flux level (0..4) from which the cap glows.</summary>
    private const int HotLevel = 3;

    protected override void OnAppearanceChange(EntityUid uid, ReactorChannelComponent component, ref AppearanceChangeEvent args)
    {
        if (args.Sprite == null)
            return;

        AppearanceSystem.TryGetData<ReactorCellType>(uid, ReactorChannelVisuals.Contents, out var contents, args.Component);
        AppearanceSystem.TryGetData<int>(uid, ReactorChannelVisuals.Flux, out var flux, args.Component);

        var state = contents switch
        {
            ReactorCellType.Fuel => "fuel",
            ReactorCellType.Rod => "rod",
            ReactorCellType.Graphite => "graphite",
            _ => "empty",
        };

        if (contents != ReactorCellType.Empty && flux >= HotLevel)
            state += "-hot";

        SpriteSystem.LayerSetRsiState((uid, args.Sprite), ReactorChannelVisuals.Contents, state);
    }
}
