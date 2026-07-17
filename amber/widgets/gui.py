from PySide6.QtGui import QFont
from .base import AObject
from amber.core import AmberProperty


class AFont(QFont, AObject):
    def __init__(self) -> None:
        QFont.__init__(self)
        AObject.__init__(self)

        self.bold_property =(
            AmberProperty[AFont, bool](self, "bold_property", self.bold, self.setBold))
        self.capitalization_property =(
            AmberProperty[AFont, QFont.Capitalization](self, "capitalization_property", self.capitalization, self.setCapitalization))
        self.families_property =(
            AmberProperty[AFont, list[str]](self, "families_property", self.families, self.setFamilies))
        self.family_property =(
            AmberProperty[AFont, str](self, "family_property", self.family, self.setFamily))
        self.fixed_pitch_property =(
            AmberProperty[AFont, bool](self, "fixed_pitch_property", self.fixedPitch, self.setFixedPitch))
        self.hinting_preference_property =(
            AmberProperty[AFont, QFont.HintingPreference](self, "hinting_preference_property", self.hintingPreference, self.setHintingPreference))
        self.italic_property =(
            AmberProperty[AFont, bool](self, "italic_property", self.italic, self.setItalic))
        self.kerning_property =(
            AmberProperty[AFont, bool](self, "kerning_property", self.kerning, self.setKerning))
        self.legacy_weight_property =(
            AmberProperty[AFont, int](self, "legacy_weight_property", self.legacyWeight, self.setLegacyWeight))
        self.overline_property =(
            AmberProperty[AFont, bool](self, "overline_property", self.overline, self.setOverline))
        self.pixel_size_property =(
            AmberProperty[AFont, int](self, "pixel_size_property", self.pixelSize, self.setPixelSize))
        self.point_size_property =(
            AmberProperty[AFont, int](self, "point_size_property", self.pointSize, self.setPointSize))
        self.point_size_f_property =(
            AmberProperty[AFont, float](self, "point_size_f_property", self.pointSizeF, self.setPointSizeF))
        self.resolve_mask_property =(
            AmberProperty[AFont, int](self, "resolve_mask_property", self.resolveMask, self.setResolveMask))
        self.stretch_property =(
            AmberProperty[AFont, int](self, "stretch_property", self.stretch, self.setStretch))
        self.strike_out_property =(
            AmberProperty[AFont, bool](self, "strike_out_property", self.strikeOut, self.setStrikeOut))
        self.style_property =(
            AmberProperty[AFont, QFont.Style](self, "style_property", self.style, self.setStyle))
        self.style_name_property =(
            AmberProperty[AFont, str](self, "style_name_property", self.styleName, self.setStyleName))
        self.style_strategy_property =(
            AmberProperty[AFont, QFont.StyleStrategy](self, "style_strategy_property", self.styleStrategy, self.setStyleStrategy))
        self.underline_property =(
            AmberProperty[AFont, bool](self, "underline_property", self.underline, self.setUnderline))
        self.weight_property =(
            AmberProperty[AFont, QFont.Weight](self, "weight_property", self.weight, self.setWeight))
        self.word_spacing_property =(
            AmberProperty[AFont, float](self, "word_spacing_property", self.wordSpacing, self.setWordSpacing))
