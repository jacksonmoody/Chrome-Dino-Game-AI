# Chrome Dino Game AI
### By Jackson Moody

Using the [NEAT Algorithm](https://neat-python.readthedocs.io/en/latest/) to evolve a neural network capable of beating the [Chrome Dino Game](https://chromedino.com/)

## Requirements
- Python 3.8 or higher
- [pygame](https://www.pygame.org/)
- [numpy](https://numpy.org/)
- [neat-python](https://neat-python.readthedocs.io/en/latest/)

## File Structure
```
Final-Project/
├── main.py
├── best_genome.pkl
├── config-feedforward.txt
```

## Running the Project
`main.py` contains the code for both playing the Dino Game and evolving the neural network. To play, ensure that you have all the requirements installed, then run the following command:

```bash
python main.py
```

To play alone, press the space bar. To play against the best-trained AI, press the "a" key. To evolve a new version of the AI, run the following command:

```bash
python main.py train
```
This will start the NEAT algorithm and train a new genome. The best genome will be saved to `best_genome.pkl` after training is complete.

## Config File
The config file `config-feedforward.txt` is used to configure the NEAT algorithm. It contains the parameters for the neural network and the evolution process. You can modify the parameters to change the evolution of the algorithm, including the activation function used. The default parameters should work well for most cases.

## Final Report
See [here](https://docs.google.com/document/d/1Ymk62-esCarto7vAbFlDCTFb6k-0kSuHs9GPJXEtUsg/edit?usp=sharing) for the full report on this project, including a literature review, specific methodology, results, and conclusions. 
