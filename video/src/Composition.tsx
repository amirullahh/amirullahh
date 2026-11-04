import React from "react";
import { AbsoluteFill, Composition, Easing, Still, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { Character } from "./Character";

/** 2-second clip: the Cloud Sage slides in, powers up the aura and waves. */
export const Wave: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  const enter = interpolate(frame, [0, 14], [0, 1], { extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) });
  const raise = interpolate(frame, [8, 20], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.back(1.4)) });
  const wave = frame > 18 ? Math.sin((frame - 18) / 3.2) * 20 : 0;
  const blink = frame >= 44 && frame <= 47 ? 1 : 0;
  const aura = interpolate(frame, [4, 22], [0.15, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <AbsoluteFill style={{ backgroundColor: "#0d0e16" }}>
      <AbsoluteFill style={{ transform: `translateX(${(1 - enter) * 140}px)`, opacity: enter }}>
        <Character pose="wave" arm={raise * 115 + wave} t={t} blink={blink} aura={aura} />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

export const Portrait: React.FC = () => <Character pose="rest" t={0.6} aura={0.9} />;
export const Point: React.FC = () => <Character pose="point" t={0.9} wink aura={1} />;

export const MyComposition = () => (
  <>
    <Composition id="Wave" component={Wave} durationInFrames={60} fps={30} width={480} height={480} />
    <Still id="Portrait" component={Portrait} width={480} height={480} />
    <Still id="Point" component={Point} width={480} height={480} />
  </>
);
