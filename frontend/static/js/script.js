document.addEventListener('DOMContentLoaded', function() {
    // Get DOM elements
    const recipeForm = document.getElementById('recipe-form');
    const ingredientsInput = document.getElementById('ingredients');
    const dietaryPreferenceSelect = document.getElementById('dietary-preference');
    const goalSelect = document.getElementById('goal');
    const generateBtn = document.getElementById('generate-btn');
    const loadingIndicator = document.getElementById('loading-indicator');
    const resultSection = document.getElementById('result-section');
    const recipeName = document.getElementById('recipe-name');
    const ingredientsList = document.getElementById('ingredients-list');
    const instructionsList = document.getElementById('instructions-list');
    const nutritionInfo = document.getElementById('nutrition-info');
    const suggestionsList = document.getElementById('suggestions-list');
    const playAudioBtn = document.getElementById('play-audio-btn');
    const recipeAudio = document.getElementById('recipe-audio');
    const audioLoadingIndicator = document.getElementById('audio-loading-indicator');

    // Add event listener for form submission
    recipeForm.addEventListener('submit', function(e) {
        e.preventDefault();
        generateRecipe();
    });

    // Add event listener for play audio button
    playAudioBtn.addEventListener('click', function() {
        generateAudio();
    });

    // Function to generate recipe
    function generateRecipe() {
        // Show loading indicator
        loadingIndicator.style.display = 'flex';
        generateBtn.disabled = true;

        // Get form values
        const ingredients = ingredientsInput.value.split(',').map(item => item.trim());
        const dietaryPreference = dietaryPreferenceSelect.value;
        const goal = goalSelect.value;

        // Prepare request data
        const requestData = {
            ingredients: ingredients,
            dietary_preference: dietaryPreference,
            goal: goal
        };

        // Show result section
        resultSection.style.display = 'block';

        // Initialize recipe structure
        const recipe = {
            name: '',
            ingredients: [],
            instructions: [],
            nutrition: {},
            suggestions: []
        };

        // Display initial empty recipe
        displayRecipe(recipe);

        // Scroll to result section
        resultSection.scrollIntoView({ behavior: 'smooth' });

        // Make API call to stream recipe
        fetch('/api/stream-recipe', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            // Get a reader from the response body stream
            const reader = response.body.getReader();

            // Accumulated content
            let accumulatedContent = '';

            // Function to process stream chunks
            function processStream() {
                // Read a chunk
                return reader.read().then(({ done, value }) => {
                    // If the stream is done, finish up
                    if (done) {
                        // Final update with complete content
                        updateRecipeDisplay(accumulatedContent, true);

                        // Hide loading indicator
                        loadingIndicator.style.display = 'none';
                        generateBtn.disabled = false;

                        return;
                    }

                    // Convert the chunk to text
                    const chunk = new TextDecoder().decode(value);

                    // Process each line (in case we get multiple SSE messages in one chunk)
                    const lines = chunk.split('\n\n');
                    for (const line of lines) {
                        if (line.startsWith('data: ')) {
                            try {
                                const data = JSON.parse(line.substring(6));
                                if (data.chunk) {
                                    // Append new chunk to accumulated content
                                    accumulatedContent += data.chunk;

                                    // Try to parse the accumulated content
                                    try {
                                        // Simple parsing to update UI incrementally
                                        updateRecipeDisplay(accumulatedContent);
                                    } catch (parseError) {
                                        console.log('Partial content not yet parseable, continuing to accumulate');
                                    }
                                }
                            } catch (error) {
                                console.error('Error processing chunk:', error);
                            }
                        }
                    }

                    // Continue processing the stream
                    return processStream();
                });
            }

            // Start processing the stream
            return processStream();
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while generating the recipe. Please try again.');

            // Hide loading indicator
            loadingIndicator.style.display = 'none';
            generateBtn.disabled = false;
        });
    }

    // Function to update recipe display incrementally
    function updateRecipeDisplay(content, isFinal = false) {
        // Simple parsing logic to extract sections from the content
        const lines = content.split('\n');
        const recipe = {
            name: '',
            ingredients: [],
            instructions: [],
            nutrition: {},
            suggestions: []
        };

        let currentSection = null;

        for (const line of lines) {
            const trimmedLine = line.trim();
            if (!trimmedLine) continue;

            // Try to identify sections
            if (trimmedLine.includes("Recipe name") || trimmedLine.startsWith("# ")) {
                recipe.name = trimmedLine.replace("Recipe name:", "").replace("# ", "").trim();
                currentSection = 'name';
            } else if (trimmedLine.includes("Ingredients") || trimmedLine.startsWith("## Ingredients")) {
                currentSection = 'ingredients';
            } else if (trimmedLine.includes("Instructions") || trimmedLine.includes("Steps") || trimmedLine.startsWith("## Instructions")) {
                currentSection = 'instructions';
            } else if (trimmedLine.includes("Nutritional") || trimmedLine.startsWith("## Nutrition")) {
                currentSection = 'nutrition';
            } else if (trimmedLine.includes("Suggestions") || trimmedLine.includes("Modifications") || trimmedLine.startsWith("## Suggestions")) {
                currentSection = 'suggestions';
            } else {
                // Add content to the current section
                if (currentSection === 'ingredients') {
                    recipe.ingredients.push(trimmedLine);
                } else if (currentSection === 'instructions') {
                    recipe.instructions.push(trimmedLine);
                } else if (currentSection === 'nutrition') {
                    // Try to parse nutrition information
                    if (trimmedLine.toLowerCase().includes("calories")) {
                        recipe.nutrition.calories = trimmedLine;
                    } else if (trimmedLine.toLowerCase().includes("protein")) {
                        recipe.nutrition.protein = trimmedLine;
                    } else if (trimmedLine.toLowerCase().includes("carbs") || trimmedLine.toLowerCase().includes("carbohydrates")) {
                        recipe.nutrition.carbs = trimmedLine;
                    } else if (trimmedLine.toLowerCase().includes("fat")) {
                        recipe.nutrition.fat = trimmedLine;
                    } else {
                        recipe.nutrition[`other_${Object.keys(recipe.nutrition).length}`] = trimmedLine;
                    }
                } else if (currentSection === 'suggestions') {
                    recipe.suggestions.push(trimmedLine);
                }
            }
        }

        // Display the recipe
        displayRecipe(recipe);
    }

    // Function to display recipe
    function displayRecipe(recipe) {
        // Display recipe name
        recipeName.textContent = recipe.name;

        // Display ingredients
        ingredientsList.innerHTML = '';
        recipe.ingredients.forEach(ingredient => {
            ingredientsList.innerHTML += marked.parse(ingredient);
        });

        // Display instructions
        instructionsList.innerHTML = '';
        recipe.instructions.forEach(instruction => {
            instructionsList.innerHTML += marked.parse(instruction);
        });

        // Display nutrition information
        nutritionInfo.innerHTML = '';
        for (const [key, value] of Object.entries(recipe.nutrition)) {
            nutritionInfo.innerHTML += marked.parse(value);
        }

        // Display suggestions
        suggestionsList.innerHTML = '';
        recipe.suggestions.forEach(suggestion => {
            suggestionsList.innerHTML += marked.parse(suggestion);
        });
    }

    // Function to generate audio
    function generateAudio() {
        // Hide audio player
        recipeAudio.style.display = 'none';

        // Show loading indicator
        audioLoadingIndicator.style.display = 'flex';
        playAudioBtn.disabled = true;

        // Prepare text for TTS
        let recipeText = "";

        // Add ingredients
        recipeText += "Ingredients: ";
        const ingredientsItems = ingredientsList.querySelectorAll('li');
        ingredientsItems.forEach((item, index) => {
            recipeText += item.textContent;
            recipeText += ";";
        });

        // Add instructions
        recipeText += "\n Instructions: \n";
        const instructionsItems = instructionsList.querySelectorAll('li');
        instructionsItems.forEach((item, index) => {
            recipeText += item.textContent;
            recipeText += "\n";
        });

        // Initialize audio queue and playback state
        window.audioQueue = [];
        window.isPlaying = false;
        window.isAudioEnded = false;
        window.streamComplete = false;

        // Make API call to stream audio URLs
        fetch('/api/stream-text-to-speech', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                text: recipeText,
                voice: 'Ethan'
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            // Get a reader from the response body stream
            const reader = response.body.getReader();

            // Buffer for incomplete chunks
            let buffer = '';

            // Function to process stream chunks
            function processStream() {
                // Read a chunk
                return reader.read().then(({ done, value }) => {
                    // If the stream is done, finish up
                    if (done) {
                        console.log('Stream complete');
                        window.streamComplete = true;

                        // If we're not playing and there are no more segments in the queue,
                        // hide the loading indicator
                        if (!window.isPlaying && window.audioQueue.length === 0) {
                            audioLoadingIndicator.style.display = 'none';
                        }
                        return;
                    }

                    // Convert the chunk to text and add to buffer
                    const chunk = new TextDecoder().decode(value);
                    buffer += chunk;

                    // Process each complete line
                    const lines = buffer.split('\n');
                    // Keep the last line in the buffer if it's incomplete
                    buffer = lines.pop() || '';

                    for (const line of lines) {
                        if (line.trim()) {
                            try {
                                const data = JSON.parse(line);

                                if (data.url) {
                                    // Add the URL to the queue
                                    window.audioQueue.push(data.url);
                                    console.log('Received audio URL:', data.url);

                                    // If not currently playing, start playback
                                    if (!window.isPlaying) {
                                        playNextAudioSegment();
                                    }
                                } else if (data.error) {
                                    // Handle error for a segment
                                    console.error('Error generating audio for segment:', data.error);

                                    // Display a small notification about the error
                                    const errorDiv = document.createElement('div');
                                    errorDiv.className = 'error-notification';
                                    errorDiv.textContent = 'Error generating audio for a segment. Continuing with next segment.';
                                    errorDiv.style.color = 'red';
                                    errorDiv.style.fontSize = '0.8em';
                                    errorDiv.style.margin = '5px 0';

                                    // Add the notification near the audio player
                                    if (recipeAudio.parentNode) {
                                        recipeAudio.parentNode.insertBefore(errorDiv, recipeAudio.nextSibling);

                                        // Remove the notification after 5 seconds
                                        setTimeout(() => {
                                            if (errorDiv.parentNode) {
                                                errorDiv.parentNode.removeChild(errorDiv);
                                            }
                                        }, 5000);
                                    }
                                } else if (data.end === true) {
                                    // All segments have been received
                                    console.log('All audio segments have been received');
                                    window.streamComplete = true;

                                    // If we're not playing and there are no more segments in the queue,
                                    // hide the loading indicator
                                    if (!window.isPlaying && window.audioQueue.length === 0) {
                                        audioLoadingIndicator.style.display = 'none';
                                    }
                                }
                            } catch (error) {
                                console.error('Error processing line:', error, line);
                            }
                        }
                    }

                    // Continue processing the stream
                    return processStream();
                });
            }

            // Start processing the stream
            return processStream();
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while generating the audio. Please try again.');
            audioLoadingIndicator.style.display = 'none';
            playAudioBtn.disabled = false;
            window.streamComplete = true;
        });

        // Handle page unload to clean up resources
        window.addEventListener('beforeunload', function() {
            // Any cleanup needed
        });
    }

    // Function to play audio segments sequentially
    function playNextAudioSegment() {
        // Check if we're already playing
        if (window.isPlaying) {
            return;
        }

        // Check if there are any URLs in the queue
        if (window.audioQueue && window.audioQueue.length > 0) {
            // Mark as playing
            window.isPlaying = true;
            window.isAudioEnded = false;

            // Get the next URL from the queue
            const nextUrl = window.audioQueue.shift();

            // Set audio source to current segment
            recipeAudio.src = nextUrl;

            // Show audio player
            recipeAudio.style.display = 'block';

            // Hide loading indicator after first segment starts playing
            audioLoadingIndicator.style.display = 'none';
            playAudioBtn.disabled = false;

            // Play audio
            recipeAudio.play().catch(error => {
                console.error('Error playing audio:', error);
                window.isPlaying = false;
                playNextAudioSegment(); // Try the next segment
            });

            // Set up event listener for when this segment ends
            recipeAudio.onended = function() {
                // Mark as not playing
                window.isPlaying = false;
                window.isAudioEnded = true;

                // Check if there are more segments in the queue
                if (window.audioQueue.length > 0) {
                    // Play the next segment
                    playNextAudioSegment();
                } else if (window.streamComplete) {
                    // No more segments and stream is complete, we're done
                    console.log('All audio segments have been played');
                } else {
                    // No more segments but stream is still active, wait for more
                    console.log('Waiting for more audio segments...');

                    // Show a small loading indicator to indicate waiting for more segments
                    audioLoadingIndicator.style.display = 'flex';
                    audioLoadingIndicator.innerHTML = '<div>Loading next segment...</div>';
                }
            };

            // Set up error handler
            recipeAudio.onerror = function() {
                console.error('Audio playback error');
                window.isPlaying = false;
                playNextAudioSegment(); // Try the next segment
            };
        } else if (window.isAudioEnded && window.streamComplete) {
            // No more segments and we've already played something, we're done
            console.log('No more audio segments to play');
            audioLoadingIndicator.style.display = 'none';
        } else {
            // No segments yet, but we're still waiting for them
            console.log('Waiting for audio segments...');
            audioLoadingIndicator.style.display = 'flex';
        }
    }
});
