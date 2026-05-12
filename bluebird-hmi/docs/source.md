# Source code reference

`bluebird-hmi` is a TypeScript/React frontend, so we do not use `mkdocstrings` here (it is currently configured for Python packages in this repo).  
This page provides a practical map of the key source modules.

## App shell and state

- `bluebird-hmi/src/main.tsx`: React entry point.
- `bluebird-hmi/src/App.tsx`: top-level application composition.
- `bluebird-hmi/src/app/store.ts`: Redux store setup.
- `bluebird-hmi/src/app/hooks.ts`: typed Redux hooks.
- `bluebird-hmi/src/slices/scenarioSlice.tsx`: scenario state and control data.
- `bluebird-hmi/src/slices/staticDataSlice.tsx`: static simulation data state.
- `bluebird-hmi/src/slices/dynamicDataSlice.tsx`: live simulation data state.
- `bluebird-hmi/src/slices/hmiDataSlice.tsx`: HMI UI state.

## API integration

- `bluebird-hmi/src/api/config.ts`: API endpoint configuration.
- `bluebird-hmi/src/api/api.ts`: request layer for backend endpoints.
- `bluebird-hmi/src/api/emptyApi.ts`: base API placeholder/RTK wiring.

## Radar and visualisation

- `bluebird-hmi/src/pages/RadarPage.tsx`: primary radar page container.
- `bluebird-hmi/src/components/Radar.tsx`: radar canvas/component orchestration.
- `bluebird-hmi/src/components/radarElements/`: rendered map/aircraft/fix/route layers.
- `bluebird-hmi/src/components/overlays/`: UI overlays such as action logs and colour bars.
- `bluebird-hmi/src/components/radarDrawer/`: drawer controls (themes, map controls, timeline, tools).

## Panels and scenario UI

- `bluebird-hmi/src/components/panel/`: side panels for scenario metadata and control.
- `bluebird-hmi/src/components/panel/items/`: reusable panel controls (buttons, switches, selectors, inputs).
- `bluebird-hmi/src/components/scenarioSelection/`: scenario/category selection and loading.
- `bluebird-hmi/src/components/infoBlock/`: aircraft/radar information block variants.

## Geometry and styling helpers

- `bluebird-hmi/src/utils/`: geometry, heading, distance, path creation, and shared types.
- `bluebird-hmi/src/utils/profiles/`: colour and line-width profiles used by radar rendering.
- `bluebird-hmi/src/components/ToolStoreHandlers.ts`: integration points for ATC tool state/actions.

