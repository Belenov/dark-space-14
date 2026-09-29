using System.Numerics;
using Content.Client.UserInterface.Controls;
using Content.Shared._DarkSpace.Reactor;
using Robust.Client.Graphics;
using Robust.Client.UserInterface.Controls;

namespace Content.Client._DarkSpace.Reactor;

/// <summary>
/// Control rod console of the ИР-7: exact readings, the core cartogram, rod controls and AZ-5.
/// </summary>
public sealed class ReactorWindow : FancyWindow
{
    public event Action<float>? OnSetRods;
    public event Action? OnScram;
    public event Action? OnResetScram;

    private static readonly Color Panel = Color.FromHex("#1c1f1a");
    private static readonly Color Amber = Color.FromHex("#ffb347");
    private static readonly Color Green = Color.FromHex("#9fe07a");
    private static readonly Color Red = Color.FromHex("#ff4d3a");

    private readonly Label _power = Readout();
    private readonly Label _keff = Readout();
    private readonly Label _core = Readout();
    private readonly Label _coolant = Readout();
    private readonly Label _rods = Readout();
    private readonly Label _integrity = Readout();
    private readonly Label _passport = new() { FontColorOverride = Color.LightGray };
    private readonly Label _alarm = new() { HorizontalAlignment = HAlignment.Center };
    private readonly GridContainer _cartogram = new() { HSeparationOverride = 2, VSeparationOverride = 2 };
    private readonly Button _scram;
    private readonly Button _reset;
    private readonly List<Button> _rodButtons = new();

    private float _target;

    public ReactorWindow()
    {
        Title = Loc.GetString("ds-reactor-ui-title");
        MinSize = new Vector2(560, 420);

        var readings = new GridContainer { Columns = 2, HSeparationOverride = 12 };
        AddRow(readings, "ds-reactor-ui-power", _power);
        AddRow(readings, "ds-reactor-ui-keff", _keff);
        AddRow(readings, "ds-reactor-ui-core", _core);
        AddRow(readings, "ds-reactor-ui-coolant", _coolant);
        AddRow(readings, "ds-reactor-ui-rods", _rods);
        AddRow(readings, "ds-reactor-ui-integrity", _integrity);

        var rodRow = new BoxContainer { Orientation = BoxContainer.LayoutOrientation.Horizontal, SeparationOverride = 4 };
        rodRow.AddChild(new Label { Text = Loc.GetString("ds-reactor-ui-rod-target"), VerticalAlignment = VAlignment.Center });
        foreach (var step in new[] { -10, -1, 1, 10 })
        {
            var delta = step / 100f;
            var button = new Button { Text = step > 0 ? $"▼ {step}%" : $"▲ {-step}%", ToolTip = Loc.GetString(step > 0 ? "ds-reactor-ui-lower" : "ds-reactor-ui-raise") };
            button.OnPressed += _ => OnSetRods?.Invoke(Math.Clamp(_target + delta, 0f, 1f));
            _rodButtons.Add(button);
            rodRow.AddChild(button);
        }

        _scram = new Button { Text = Loc.GetString("ds-reactor-verb-scram"), MinSize = new Vector2(120, 40), ModulateSelfOverride = Red };
        _scram.OnPressed += _ => OnScram?.Invoke();
        _reset = new Button { Text = Loc.GetString("ds-reactor-verb-reset"), Visible = false };
        _reset.OnPressed += _ => OnResetScram?.Invoke();

        var left = new BoxContainer
        {
            Orientation = BoxContainer.LayoutOrientation.Vertical,
            SeparationOverride = 8,
            HorizontalExpand = true,
            Children = { readings, _passport, rodRow, _alarm },
        };

        var right = new BoxContainer
        {
            Orientation = BoxContainer.LayoutOrientation.Vertical,
            SeparationOverride = 8,
            Children =
            {
                new Label { Text = Loc.GetString("ds-reactor-ui-cartogram"), HorizontalAlignment = HAlignment.Center },
                _cartogram,
                _scram,
                _reset,
            },
        };

        ContentsContainer.AddChild(new PanelContainer
        {
            PanelOverride = new StyleBoxFlat { BackgroundColor = Panel },
            Children =
            {
                new BoxContainer
                {
                    Orientation = BoxContainer.LayoutOrientation.Horizontal,
                    SeparationOverride = 16,
                    Margin = new Thickness(10),
                    Children = { left, right },
                },
            },
        });
    }

    private static Label Readout()
    {
        return new Label { FontColorOverride = Amber };
    }

    private static void AddRow(GridContainer grid, string loc, Label value)
    {
        grid.AddChild(new Label { Text = Loc.GetString(loc) });
        grid.AddChild(value);
    }

    public void UpdateState(ReactorUiState s)
    {
        _target = s.TargetRodInsertion;

        _power.Text = $"{s.Power / 1000f:F1} кВт ({s.Power / s.NominalPower:P0} ном.)";
        _keff.Text = s.KEff.ToString("F4");
        _keff.FontColorOverride = s.KEff > 1.005f ? Red : s.KEff < 0.995f ? Color.LightBlue : Green;
        _core.Text = $"{s.CoreTemperature:F0} K / {s.MeltdownTemperature:F0} K";
        _core.FontColorOverride = s.CoreTemperature > s.WarningTemperature ? Red : Amber;
        _coolant.Text = s.CoolantTemperature is { } t ? $"{t:F0} K" : Loc.GetString("ds-reactor-ui-no-coolant");
        _rods.Text = $"{s.RodInsertion:P0} (задано {s.TargetRodInsertion:P0})";
        _integrity.Text = $"{s.Integrity:F0}%";
        _integrity.FontColorOverride = s.Integrity < 100f ? Red : Green;
        _passport.Text = Loc.GetString("ds-reactor-ui-passport",
            ("batch", s.BatchNumber),
            ("k", s.PassportReproduction.ToString("F3")),
            ("error", (int) MathF.Round(s.PassportError * 100)));

        if (s.Melted)
            SetAlarm("ds-reactor-examine-melted-plain");
        else if (s.Scrammed)
            SetAlarm("ds-reactor-ui-scrammed");
        else if (s.CoreTemperature > s.WarningTemperature)
            SetAlarm("ds-reactor-warning-overheat");
        else
            _alarm.Text = string.Empty;

        _scram.Visible = !s.Scrammed && !s.Melted;
        _reset.Visible = s.Scrammed && !s.Melted;
        foreach (var button in _rodButtons)
            button.Disabled = s.Scrammed || s.Melted;

        UpdateCartogram(s);
    }

    private void SetAlarm(string loc)
    {
        _alarm.Text = Loc.GetString(loc);
        _alarm.FontColorOverride = Red;
    }

    private void UpdateCartogram(ReactorUiState s)
    {
        _cartogram.Columns = s.Size;
        _cartogram.RemoveAllChildren();

        foreach (var cell in s.Cells)
        {
            var (letter, color) = cell switch
            {
                ReactorCellType.Fuel => ("Т", Color.FromHex("#c8792a")),
                ReactorCellType.Rod => ("С", Color.InterpolateBetween(Color.FromHex("#3a6ea5"), Color.FromHex("#101828"), s.RodInsertion)),
                ReactorCellType.Graphite => ("Г", Color.FromHex("#4a4a4a")),
                _ => ("·", Color.FromHex("#26291f")),
            };

            _cartogram.AddChild(new PanelContainer
            {
                MinSize = new Vector2(36, 36),
                PanelOverride = new StyleBoxFlat { BackgroundColor = color },
                Children = { new Label { Text = letter, HorizontalAlignment = HAlignment.Center, VerticalAlignment = VAlignment.Center } },
            });
        }
    }
}
