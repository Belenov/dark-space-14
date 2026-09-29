using System.Numerics;
using Content.Client.UserInterface.Controls;
using Content.Shared._DarkSpace.Reactor;
using Robust.Client.Graphics;
using Robust.Client.UserInterface;
using Robust.Client.UserInterface.Controls;

namespace Content.Client._DarkSpace.Reactor;

/// <summary>
/// Пульт СУЗ: the channel cartogram with power per channel on the left,
/// exact readings on the right, rod controls and AZ-5 below.
/// </summary>
public sealed class ReactorWindow : FancyWindow
{
    public event Action<float>? OnSetRods;
    public event Action? OnScram;
    public event Action? OnResetScram;

    private static readonly Color Panel = Color.FromHex("#1a1d18");
    private static readonly Color Bezel = Color.FromHex("#2b2f27");
    private static readonly Color Amber = Color.FromHex("#ffb347");
    private static readonly Color Green = Color.FromHex("#9fe07a");
    private static readonly Color Red = Color.FromHex("#ff4d3a");
    private static readonly Color Dim = Color.FromHex("#8a9080");

    private const float CellSize = 52f;

    private readonly Label _power = Readout();
    private readonly Label _keff = Readout();
    private readonly Label _core = Readout();
    private readonly Label _coolant = Readout();
    private readonly Label _rods = Readout();
    private readonly Label _integrity = Readout();
    private readonly Label _batch = Readout();
    private readonly Label _reproduction = Readout();
    private readonly Label _alarm = new() { HorizontalAlignment = HAlignment.Center, FontColorOverride = Red };
    private readonly GridContainer _cartogram = new() { HSeparationOverride = 3, VSeparationOverride = 3 };
    private readonly Button _scram;
    private readonly Button _reset;
    private readonly List<Button> _rodButtons = new();
    private readonly BoxContainer _body;
    private readonly Label _unlinked;

    private float _target;

    public ReactorWindow()
    {
        Title = Loc.GetString("ds-reactor-ui-title");
        MinSize = new Vector2(820, 560);

        var readings = new GridContainer { Columns = 2, HSeparationOverride = 16, VSeparationOverride = 6 };
        AddRow(readings, "ds-reactor-ui-power", _power);
        AddRow(readings, "ds-reactor-ui-keff", _keff);
        AddRow(readings, "ds-reactor-ui-core", _core);
        AddRow(readings, "ds-reactor-ui-coolant", _coolant);
        AddRow(readings, "ds-reactor-ui-rods", _rods);
        AddRow(readings, "ds-reactor-ui-integrity", _integrity);

        var passport = new GridContainer { Columns = 2, HSeparationOverride = 16, VSeparationOverride = 6 };
        AddRow(passport, "ds-reactor-ui-batch", _batch);
        AddRow(passport, "ds-reactor-ui-reproduction", _reproduction);

        var rodRow = new BoxContainer { Orientation = BoxContainer.LayoutOrientation.Horizontal, SeparationOverride = 6 };
        foreach (var step in new[] { -10, -1, 1, 10 })
        {
            var delta = step / 100f;
            var button = new Button
            {
                Text = step > 0 ? $"▼ {step}%" : $"▲ {-step}%",
                ToolTip = Loc.GetString(step > 0 ? "ds-reactor-ui-lower" : "ds-reactor-ui-raise"),
                MinSize = new Vector2(64, 32),
            };
            button.OnPressed += _ => OnSetRods?.Invoke(Math.Clamp(_target + delta, 0f, 1f));
            _rodButtons.Add(button);
            rodRow.AddChild(button);
        }

        _scram = new Button
        {
            Text = Loc.GetString("ds-reactor-verb-scram"),
            MinSize = new Vector2(0, 56),
            HorizontalExpand = true,
            ModulateSelfOverride = Red,
        };
        _scram.OnPressed += _ => OnScram?.Invoke();

        _reset = new Button { Text = Loc.GetString("ds-reactor-verb-reset"), MinSize = new Vector2(0, 56), HorizontalExpand = true, Visible = false };
        _reset.OnPressed += _ => OnResetScram?.Invoke();

        var right = new BoxContainer
        {
            Orientation = BoxContainer.LayoutOrientation.Vertical,
            SeparationOverride = 10,
            HorizontalExpand = true,
            MinWidth = 330,
            Children =
            {
                Section("ds-reactor-ui-section-readings", readings),
                Section("ds-reactor-ui-section-passport", passport),
                Section("ds-reactor-ui-section-rods", rodRow),
                new Control { VerticalExpand = true },
                _alarm,
                _scram,
                _reset,
            },
        };

        var left = Section("ds-reactor-ui-cartogram", _cartogram);

        _body = new BoxContainer
        {
            Orientation = BoxContainer.LayoutOrientation.Horizontal,
            SeparationOverride = 16,
            Margin = new Thickness(12),
            Children = { left, right },
        };

        _unlinked = new Label
        {
            Text = Loc.GetString("ds-reactor-ui-unlinked"),
            HorizontalAlignment = HAlignment.Center,
            VerticalAlignment = VAlignment.Center,
            FontColorOverride = Dim,
            Visible = false,
        };

        ContentsContainer.AddChild(new PanelContainer
        {
            PanelOverride = new StyleBoxFlat { BackgroundColor = Panel },
            Children = { _body, _unlinked },
        });
    }

    private static Label Readout()
    {
        return new Label { FontColorOverride = Amber, ClipText = false };
    }

    private static void AddRow(GridContainer grid, string loc, Label value)
    {
        grid.AddChild(new Label { Text = Loc.GetString(loc), FontColorOverride = Dim });
        grid.AddChild(value);
    }

    private static Control Section(string title, Control content)
    {
        return new PanelContainer
        {
            PanelOverride = new StyleBoxFlat { BackgroundColor = Bezel, ContentMarginLeftOverride = 10, ContentMarginRightOverride = 10, ContentMarginTopOverride = 6, ContentMarginBottomOverride = 8 },
            Children =
            {
                new BoxContainer
                {
                    Orientation = BoxContainer.LayoutOrientation.Vertical,
                    SeparationOverride = 6,
                    Children =
                    {
                        new Label { Text = Loc.GetString(title), FontColorOverride = Amber },
                        content,
                    },
                },
            },
        };
    }

    public void UpdateState(ReactorUiState s)
    {
        _body.Visible = s.Linked;
        _unlinked.Visible = !s.Linked;
        if (!s.Linked)
            return;

        _target = s.TargetRodInsertion;

        _power.Text = Loc.GetString("ds-reactor-ui-power-value",
            ("kw", (s.Power / 1000f).ToString("F1")),
            ("percent", (int) MathF.Round(s.Power / s.NominalPower * 100)));
        _keff.Text = s.KEff.ToString("F4");
        _keff.FontColorOverride = s.KEff > 1.005f ? Red : s.KEff < 0.995f ? Color.LightBlue : Green;
        _core.Text = $"{s.CoreTemperature:F0} K / {s.MeltdownTemperature:F0} K";
        _core.FontColorOverride = s.CoreTemperature > s.WarningTemperature ? Red : Amber;
        _coolant.Text = s.CoolantTemperature is { } t ? $"{t:F0} K" : Loc.GetString("ds-reactor-ui-no-coolant");
        _coolant.FontColorOverride = s.CoolantTemperature == null ? Red : Amber;
        _rods.Text = Loc.GetString("ds-reactor-ui-rods-value",
            ("rods", (int) MathF.Round(s.RodInsertion * 100)),
            ("target", (int) MathF.Round(s.TargetRodInsertion * 100)));
        _integrity.Text = $"{s.Integrity:F0}%";
        _integrity.FontColorOverride = s.Integrity < 100f ? Red : Green;
        _batch.Text = $"№{s.BatchNumber}";
        _reproduction.Text = $"{s.PassportReproduction:F3} ±{MathF.Round(s.PassportError * 100):F0}%";

        if (s.Melted)
            _alarm.Text = Loc.GetString("ds-reactor-examine-melted-plain");
        else if (s.Scrammed)
            _alarm.Text = Loc.GetString("ds-reactor-ui-scrammed");
        else if (s.CoreTemperature > s.WarningTemperature)
            _alarm.Text = Loc.GetString("ds-reactor-warning-overheat");
        else
            _alarm.Text = string.Empty;

        _scram.Visible = !s.Scrammed && !s.Melted;
        _reset.Visible = s.Scrammed && !s.Melted;
        foreach (var button in _rodButtons)
            button.Disabled = s.Scrammed || s.Melted;

        UpdateCartogram(s);
    }

    private void UpdateCartogram(ReactorUiState s)
    {
        _cartogram.Columns = Math.Max(1, s.Size);
        _cartogram.RemoveAllChildren();

        var fuel = 0;
        foreach (var cell in s.Cells)
        {
            if (cell == ReactorCellType.Fuel)
                fuel++;
        }

        var nominalChannel = s.NominalPower / Math.Max(1, fuel);

        for (var i = 0; i < s.Cells.Count; i++)
        {
            var cell = s.Cells[i];
            var flux = i < s.Flux.Count ? s.Flux[i] : 0f;
            var heat = Math.Clamp(flux / nominalChannel / 2f, 0f, 1f);

            var (letter, color) = cell switch
            {
                ReactorCellType.Fuel => ("Т", Color.InterpolateBetween(Color.FromHex("#4a3a24"), Color.FromHex("#ffd27a"), heat)),
                ReactorCellType.Rod => ("С", Color.InterpolateBetween(Color.FromHex("#3a6ea5"), Color.FromHex("#101828"), s.RodInsertion)),
                ReactorCellType.Graphite => ("Г", Color.FromHex("#3c3c3c")),
                _ => ("·", Color.FromHex("#23261f")),
            };

            var box = new BoxContainer
            {
                Orientation = BoxContainer.LayoutOrientation.Vertical,
                HorizontalAlignment = HAlignment.Center,
                VerticalAlignment = VAlignment.Center,
                Children = { new Label { Text = letter, HorizontalAlignment = HAlignment.Center, FontColorOverride = Color.White } },
            };

            if (cell == ReactorCellType.Fuel)
            {
                box.AddChild(new Label
                {
                    Text = $"{flux / 1000f:F0}",
                    HorizontalAlignment = HAlignment.Center,
                    FontColorOverride = heat > 0.6f ? Color.Black : Amber,
                });
            }

            _cartogram.AddChild(new PanelContainer
            {
                MinSize = new Vector2(CellSize, CellSize),
                ToolTip = cell == ReactorCellType.Fuel ? Loc.GetString("ds-reactor-ui-channel-tooltip", ("kw", (flux / 1000f).ToString("F1"))) : null,
                PanelOverride = new StyleBoxFlat { BackgroundColor = color },
                Children = { box },
            });
        }
    }
}
