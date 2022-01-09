# Changelog

## [Unreleased](https://github.com/amrit3701/FreeCAD-Reinforcement/tree/HEAD)
[Full Changelog](https://github.com/amrit3701/FreeCAD-Reinforcement/compare/v0.3...HEAD)

## [v0.3](https://github.com/amrit3701/FreeCAD-Reinforcement/tree/v0.3) (2022-01-09)

[Full Changelog](https://github.com/amrit3701/FreeCAD-Reinforcement/compare/v0.2..v0.3)

**Implemented features:**
- Implemented Slab reinforcement.
- Implemented Footing reinforcement.
- Improved translations.
- Sorted bar bending schedule wrt to bar mark.

## [v0.2](https://github.com/amrit3701/FreeCAD-Reinforcement/tree/v0.2) (2021-02-13)

[Full Changelog](https://github.com/amrit3701/FreeCAD-Reinforcement/compare/v0.1..v0.2)

**Implemented features:**
- Implemented reinforcement drawing dimension UI.

**UI improvements:**
- Fixed stylesheet issue in beam and column reinforcement dialog.
- Updated helping image in beam reinforcement dialog box.
- Update workbench wiki image (include drawing icon).

**Refactoring and bug fixes:**
- Fix type annotation issue `typing.Literal` bug (made code compatible Python `3.7` version).
- Fixed bug in rebar distribution through spacing.
- Fixed custom spacing issue (load custom spacing when editing column/beam Reinforcement).
- Fixed rebar points calculations when left/rear/bottom face selected.

## [v0.1](https://github.com/amrit3701/FreeCAD-Reinforcement/tree/v0.1) (2020-09-28)

[Full Changelog](https://github.com/amrit3701/FreeCAD-Reinforcement/compare/421c376da219c2872428a89190b4cc2a6f310737...v0.1)

**Implemented features:**

- Create Straight, UShape, LShape,  BentShape, Stirrup and Helical shape reinforcement bars.
- Implement circular and rectangular column reinforcement.
- Implement beam reinforcement.
- Implement generating bill Of material, rebar shape cut list, bar bending schedule and drawing and dimensioning of reinforcing bars.
