# GLOW - Graph-Lowering (Facebook)

Glow is a machine learning compiler for heterogeneous hardware developed by Google. The Glow compiler takes a traditional neural network and two-phase lowering of the graph into a strongly typed intermediate representation (IR). The high-level IR is then used for domain specific optimizations, and the lower-level IR is used for instruction-based address-only optimizations, such as memory-related optimizations. The Glow low-level graph does not replace the initial ML high-level graph. 

## High-level IR

The high-level IR consists of a dataflow node-based graph representation, similar to that of the Caffe framework. It is strongly-typed, with the tensor type consisting of the tensor shape and element type. The high-level IR graph allows for the replacement of all uses of some node with another node, or the modifying of the content of input tensor known at compile time. 

While it is strictly strongly typed, on production systems multiple Glow graphs can be generated for the same initial graph, but using different batch sizes.  

## Predication

Predication is a method of controlling node or instruction execution via the use of boolean flags. If the boolean is set to false, the node or instruction is skipped. This is used by Glow for further acceleration.

## Node lowering

Node lowering is performed by the compiler breaking down high-level operator nodes into low-level linear algebra operator nodes. For example, the fully-connect network layer can be broken down into a matrix multiplication and a broadcasted add. In Glow, node lowering is performed as part of the high-level graph - right after graph differentiation - before moving to the low-level graph. Node lowering does not preserve semantics of graph.

## Low-level IR

Once the high-level graph is node lowered into its linear algebra operator nodes, further lowering to the low-level IR phase "IRGen" is performed. IRGen - IR generation - is a one-to-many translation that outputs an instruction-based representation that operates on tensors referenced by address. This allows for low-level memory optimizations and for the compiler to create schedules hat hide latency of memory operations. 

The low-level graph is strongly-typed. It is presented in in-memory form, but can be dumped to a human readable form. Functions in this IR form contain mainly "declare" and "program" sections. 


## Summary of Glow workflow

The high-level view of the compilation process is as follows:

1. Existing graph is loaded (ONNX, Caffe2) or constructed via C++ interface 
2. graph is differentiated if needed
3. graph is optimized
4. linear algebra node lowering
5. additional rounds of optimization
6. graph scheduled into linear sequence of nodes that minimize memory usage
7. IRGen converts low-level graph into instructions
8. low-level IR optimizations
9 backend-specific optimizations and code generation.

## Quantization

For additional speed-ups, Glow converts the neural network from floating point to integer arithmetic where possible. This is performed using profile-guided quantization; training-based quantization is considered future work.

## CPU-backend

The Glow CPU backend compiles the low-level IR into optimized streams of instructions. This is done using LLVM. Glow can also emit stand-alone object files or execute code in JIT mode. The CPU backend employs operator stacking of data-parallel operators.

## Glow runtime

The Glow runtime consists of the partitioner, the provisioner, the device manager, and the executioner. The partitioner splits the graph into common subgraphs. 

## Links:

Glow: Graph Lowering Compiler Techniques for Neural Networks - https://arxiv.org/pdf/1805.00907.pdf
Glow - Graph Lowering Compiler for Hardware Accelerators - workshop talk - https://drive.google.com/file/d/1-Nczf_gXOvtjYL3ooyRFu205ivswBHAk/view
