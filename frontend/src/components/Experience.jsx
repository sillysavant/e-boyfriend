import {
  CameraControls,
  ContactShadows,
  Environment,
  Text,
} from "@react-three/drei";
import { Suspense, useEffect, useRef, useState } from "react";
import { useChat } from "../hooks/useChat";
import { Avatar } from "./Avatar";
import { AvatarBoy } from "./AvatarBoy";
import { Girlfriend } from "./Girlfriend";

const Dots = (props) => {
  const { loading } = useChat();
  const [loadingText, setLoadingText] = useState("");
  useEffect(() => {
    if (loading) {
      const interval = setInterval(() => {
        setLoadingText((loadingText) => {
          if (loadingText.length > 2) {
            return ".";
          }
          return loadingText + ".";
        });
      }, 800);
      return () => clearInterval(interval);
    } else {
      setLoadingText("");
    }
  }, [loading]);
  if (!loading) return null;
  return (
    <group {...props}>
      <Text fontSize={0.14} anchorX={"left"} anchorY={"bottom"}>
        {loadingText}
        <meshBasicMaterial attach="material" color="black" />
      </Text>
    </group>
  );
};

export const Experience = () => {
  const cameraControls = useRef();
  const { zoomLevel } = useChat();

  useEffect(() => {
    // Different positions based on zoom level
    const zoomPositions = {
      0: [0, 1.5, 5, 0, 1.0, 0], // Default view
      1: [0, 1.0, 1.5, 0, 1.0, 0], // First zoom
      2: [0, 0.8, 1.0, 0, 1.0, 0], // Closer
      3: [0, 0.6, 0.7, 0, 1.0, 0], // Very close
    };

    const [px, py, pz, tx, ty, tz] = zoomPositions[zoomLevel];
    cameraControls.current.setLookAt(px, py, pz, tx, ty, tz, true);
  }, [zoomLevel]);

  return (
    <>
      <CameraControls ref={cameraControls} />
      <Environment preset="sunset" />
      <Suspense>
        <Dots position-y={1.25} position-x={-0.02} />
      </Suspense>
      <Girlfriend position-y={-0.5} />
      <ContactShadows opacity={0.7} />
    </>
  );
};
