// Entry point for CM6 bundle — re-exports everything editor.js needs
export { EditorView, basicSetup } from "codemirror";
export { EditorState } from "@codemirror/state";
export { keymap } from "@codemirror/view";
export { indentWithTab } from "@codemirror/commands";
export { python } from "@codemirror/lang-python";
export { HighlightStyle, syntaxHighlighting } from "@codemirror/language";
export { tags } from "@lezer/highlight";
