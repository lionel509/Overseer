# Overseer CLI Demo

This directory contains a self-running demo of the Overseer CLI.

## How to Run the Demo

There are two versions of the demo available:

### 1. Standard Demo

This demo shows the user-facing experience of the Overseer CLI.

To run the standard demo, execute the following command from the root of the project:

```bash
bash demo/run_demo.sh
```

### 2. Demo with LLM Output

This demo provides a "behind-the-scenes" look at the AI's reasoning process.

To run this version, execute:

```bash
bash demo/run_demo_with_llm.sh
```

Both scripts will:

1.  **Start Recording:** The `script` command will start recording the terminal session.
2.  **Run the Demo:** The corresponding Python script will be executed.
3.  **Save the Recording:** The recording will be saved in the `demo/output/` directory.

You can then view the recording to see the full demo.
