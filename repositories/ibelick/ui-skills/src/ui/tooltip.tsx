import { Tooltip as TooltipPrimitive } from "@base-ui/react/tooltip";
import type { ReactElement, ReactNode } from "react";

type TooltipProps = {
  content: ReactNode;
  children: ReactElement;
  side?: "top" | "bottom" | "left" | "right";
};

export function TooltipProvider({ children }: { children: ReactNode }) {
  return (
    <TooltipPrimitive.Provider delay={0} closeDelay={0}>
      {children}
    </TooltipPrimitive.Provider>
  );
}

export function Tooltip({ content, children, side = "bottom" }: TooltipProps) {
  return (
    <TooltipPrimitive.Root>
      <TooltipPrimitive.Trigger delay={0} render={children} />
      <TooltipPrimitive.Portal>
        <TooltipPrimitive.Positioner side={side} sideOffset={6}>
          <TooltipPrimitive.Popup className="z-50 rounded-[6px] border-0 bg-black px-2 py-1 text-xs font-medium text-white shadow-none">
            {content}
          </TooltipPrimitive.Popup>
        </TooltipPrimitive.Positioner>
      </TooltipPrimitive.Portal>
    </TooltipPrimitive.Root>
  );
}
