import { useFrame, useThree } from "@react-three/fiber";
import { useEffect, useLayoutEffect, useMemo } from "react";
import {
  BloomEffect,
  ChromaticAberrationEffect,
  EffectComposer,
  EffectPass,
  RenderPass,
  ToneMappingEffect,
  ToneMappingMode,
  VignetteEffect,
} from "postprocessing";
import { HalfFloatType, Vector2 } from "three";

// Built synchronously, unlike @react-three/postprocessing's composer, so the very first frame
// Remotion captures is already bloomed. It renders from useFrame, which Remotion's ThreeCanvas
// drives once per video frame.

type Props = {
  bloom: number;
  threshold?: number;
  aberration?: number;
  vignette?: number;
};

export const Post: React.FC<Props> = ({ bloom, threshold = 0.12, aberration = 0, vignette = 0.55 }) => {
  const gl = useThree((s) => s.gl);
  const scene = useThree((s) => s.scene);
  const camera = useThree((s) => s.camera);
  const size = useThree((s) => s.size);

  const fx = useMemo(() => {
    const composer = new EffectComposer(gl, { frameBufferType: HalfFloatType, multisampling: 4 });
    composer.addPass(new RenderPass(scene, camera));
    const bloomFx = new BloomEffect({
      mipmapBlur: true,
      intensity: 1,
      luminanceThreshold: threshold,
      luminanceSmoothing: 0.25,
      radius: 0.78,
      levels: 9,
    });
    const chroma = new ChromaticAberrationEffect({ offset: new Vector2(0, 0), radialModulation: true, modulationOffset: 0.2 });
    const tone = new ToneMappingEffect({ mode: ToneMappingMode.AGX });
    const vig = new VignetteEffect({ offset: 0.32, darkness: vignette });
    composer.addPass(new EffectPass(camera, bloomFx));
    composer.addPass(new EffectPass(camera, chroma, tone, vig));
    return { composer, bloomFx, chroma, vig };
    // Rebuild only if the renderer, scene or camera change.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [gl, scene, camera]);

  useLayoutEffect(() => {
    fx.composer.setSize(size.width, size.height);
  }, [fx, size.width, size.height]);

  useLayoutEffect(() => {
    fx.bloomFx.intensity = bloom;
    fx.bloomFx.luminanceMaterial.threshold = threshold;
    fx.chroma.offset.set(aberration, aberration * 0.6);
    fx.vig.darkness = vignette;
  });

  useEffect(() => () => fx.composer.dispose(), [fx]);

  useFrame(() => {
    fx.composer.render();
  }, 1);

  return null;
};
