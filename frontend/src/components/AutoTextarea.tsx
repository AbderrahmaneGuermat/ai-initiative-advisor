import { useEffect, useRef } from "react";

/**
 * A textarea that grows to fit its content.
 *
 * The walkthrough showed objectives, constraint values and initiative
 * descriptions clipped in single-line inputs, so a manager could not read the
 * text they were about to send. Nothing is truncated here: the control grows
 * instead, up to a generous ceiling, after which it scrolls.
 */
export default function AutoTextarea({
  value,
  onChange,
  placeholder,
  minRows = 1,
  maxHeight = 320,
  id,
  ariaLabel,
}: {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  minRows?: number;
  maxHeight?: number;
  id?: string;
  ariaLabel?: string;
}) {
  const ref = useRef<HTMLTextAreaElement>(null);

  const resize = () => {
    const node = ref.current;
    if (!node) return;
    node.style.height = "auto";
    node.style.height = `${Math.min(node.scrollHeight, maxHeight)}px`;
    node.style.overflowY = node.scrollHeight > maxHeight ? "auto" : "hidden";
  };

  useEffect(resize, [value, maxHeight]);

  return (
    <textarea
      ref={ref}
      id={id}
      aria-label={ariaLabel}
      className="field__input field__input--auto"
      rows={minRows}
      placeholder={placeholder}
      value={value}
      onChange={(event) => {
        onChange(event.target.value);
        resize();
      }}
    />
  );
}
