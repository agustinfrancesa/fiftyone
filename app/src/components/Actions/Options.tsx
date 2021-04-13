import React from "react";
import { constSelector, useRecoilState } from "recoil";
import { Autorenew } from "@material-ui/icons";

import Popout from "./Popout";
import { PopoutSectionTitle, TabOption } from "../utils";
import * as atoms from "../../recoil/atoms";
import { Button } from "../FieldsSidebar";
import { gridZoom } from "../Samples.hooks";
import { useTheme } from "../../utils/hooks";
import { Slider } from "../Filters/RangeSlider";

const GridSizer = () => {
  const theme = useTheme();
  return (
    <>
      <PopoutSectionTitle>Zoom</PopoutSectionTitle>
      <Slider
        valueAtom={gridZoom}
        boundsAtom={constSelector([1, 9])}
        color={theme.brand}
        showNumbers={false}
      />
    </>
  );
};

export const RefreshButton = ({ modal }) => {
  const [colorSeed, setColorSeed] = useRecoilState(
    atoms.colorSeed(Boolean(modal))
  );
  return (
    <>
      <PopoutSectionTitle></PopoutSectionTitle>
      <Button
        text={"Refresh colors"}
        onClick={() => setColorSeed(colorSeed + 1)}
        style={{
          margin: "0.5rem -0.5rem",
          height: "2rem",
          borderRadius: 0,
        }}
      >
        <Autorenew
          style={{ height: "1.5rem", marginTop: "0.1rem", color: "inherit" }}
        />
      </Button>
    </>
  );
};

const ColorBy = ({ modal }) => {
  const [colorByLabel, setColorByLabel] = useRecoilState(
    atoms.colorByLabel(modal)
  );

  return (
    <>
      <PopoutSectionTitle>Color by</PopoutSectionTitle>
      <TabOption
        active={colorByLabel ? "value" : "field"}
        options={[
          {
            text: "value",
            title: "color by value",
            onClick: () => !colorByLabel && setColorByLabel(true),
          },
          {
            text: "field",
            title: "color by field",
            onClick: () => colorByLabel && setColorByLabel(false),
          },
        ]}
      />
    </>
  );
};

type OptionsProps = {
  modal: boolean;
};

const Options = ({ modal, bounds }: OptionsProps) => {
  return (
    <Popout modal={modal} bounds={bounds}>
      {!modal && <GridSizer />}
      <ColorBy modal={modal} />
      <RefreshButton modal={modal} />
    </Popout>
  );
};

export default React.memo(Options);
