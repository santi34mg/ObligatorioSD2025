import {
  createContext,
  useContext,
  useRef,
  type ReactNode,
  useCallback,
  useState,
} from "react";

interface ToastContextType {
  toastContainerRef: React.RefObject<HTMLElement | null> | null;
  setToastContainer: (ref: HTMLElement | null) => void;
}

const ToastContext = createContext<ToastContextType>({
  toastContainerRef: null,
  setToastContainer: () => {},
});

export function ToastProvider({ children }: { children: ReactNode }) {
  const defaultContainerRef = useRef<HTMLElement>(null);
  const [customContainer, setCustomContainer] = useState<HTMLElement | null>(
    null
  );
  const customContainerRef = useRef<HTMLElement | null>(null);

  const setToastContainer = useCallback((ref: HTMLElement | null) => {
    customContainerRef.current = ref;
    setCustomContainer(ref);
  }, []);

  // Use custom container if set, otherwise use default
  const activeRef = customContainer ? customContainerRef : defaultContainerRef;

  return (
    <ToastContext.Provider
      value={{ toastContainerRef: activeRef, setToastContainer }}
    >
      {children}
    </ToastContext.Provider>
  );
}

export function useToastContainer() {
  return useContext(ToastContext);
}
