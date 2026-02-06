import React from "react";
import { registerRoot, Composition as RemotionComposition } from "remotion";
import { Composition } from "./Composition";

const Root = () => {
  return (
    <RemotionComposition
      id="OverwatchQueueNotifier"
      component={Composition}
      durationInFrames={2700}
      fps={30}
      width={1920}
      height={1080}
      defaultProps={{
        version: "full",
      }}
    />
  );
};

registerRoot(Root);
