/**
 * The product, its stages, and the part loaded in it today.
 *
 * Three different things, and the shell keeps them apart. Collapsing them puts a part's name where
 * the product's belongs, and makes one component look like the whole tool.
 */

export const VENDOR = {
  name: "ZenryxAI",
  tagline: "Generate. Learn. Optimize.",
} as const;

export const PRODUCT = {
  name: "fastcad",
} as const;

/**
 * The stages, in the order the work happens: what the engineer brought, then the architectures
 * fastcad proposes on it, the ones that survive manufacturing and physics, and the set that goes
 * out as training data.
 *
 * Every stage is shown whether or not it is built. A shell that hides its unbuilt stages describes
 * a tool; one that shows them describes a product, and says where the work now leads.
 */
export type View = "extract" | "input" | "generate" | "qualify" | "dataset";

export const VIEWS: { id: View; label: string; summary: string; ready: boolean }[] = [
  {
    id: "extract",
    label: "Extract",
    summary: "Choose the folder a run reads, and tick the files in it that count.",
    ready: true,
  },
  {
    id: "input",
    label: "Input",
    summary:
      "What a run reads: the drawing, the CAD it edits, and the solver deck whose named groups say " +
      "what the analysis drives - read, never assumed.",
    ready: true,
  },
  {
    id: "generate",
    label: "Generate",
    summary:
      "Architectures proposed on the canvas - collars, bridges, tie rails, bore-to-flange paths - " +
      "each built by an operator that knows what it made.",
    ready: false,
  },
  {
    id: "qualify",
    label: "Qualify",
    summary:
      "What survives: manufacturable, the interfaces untouched, and solved on the same deck the " +
      "baseline used.",
    ready: false,
  },
  {
    id: "dataset",
    label: "Dataset",
    summary: "The designs kept, and the seat motions and gear-mesh leads they yield for training.",
    ready: false,
  },
];

/**
 * The supplied lockup is stacked - crane over wordmark over tagline - and a stacked lockup cannot
 * work in a horizontal bar: at any height that fits, the tagline degrades to a grey smudge. So the
 * crane is the mark, and the wordmark and tagline are live text beside it, which stays crisp at
 * any size and scales with the type.
 */
export const ART = {
  /** The crane, cropped out of the full lockup. */
  mark: "/zenryx-mark.png",
  /** The full stacked lockup, for anywhere it can be shown at size. */
  lockup: "/zenryx-logo.png",
} as const;
