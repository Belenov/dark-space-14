using Content.Shared._DarkSpace.Reactor;
using JetBrains.Annotations;
using Robust.Client.UserInterface;

namespace Content.Client._DarkSpace.Reactor;

[UsedImplicitly]
public sealed class ReactorBoundUserInterface(EntityUid owner, Enum uiKey) : BoundUserInterface(owner, uiKey)
{
    private ReactorWindow? _window;

    protected override void Open()
    {
        base.Open();

        _window = this.CreateWindow<ReactorWindow>();
        _window.OnSetRods += target => SendMessage(new ReactorSetRodsMessage(target));
        _window.OnScram += () => SendMessage(new ReactorScramMessage());
        _window.OnResetScram += () => SendMessage(new ReactorResetScramMessage());
    }

    protected override void UpdateState(BoundUserInterfaceState state)
    {
        base.UpdateState(state);

        if (state is ReactorUiState cast)
            _window?.UpdateState(cast);
    }
}
