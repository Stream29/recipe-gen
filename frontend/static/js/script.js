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

        // Make API call to generate recipe
        fetch('/api/generate-recipe', {
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
            return response.json();
        })
        .then(data => {
            // Display the recipe
            displayRecipe(data);

            // Hide loading indicator
            loadingIndicator.style.display = 'none';
            generateBtn.disabled = false;

            // Show result section
            resultSection.style.display = 'block';

            // Scroll to result section
            resultSection.scrollIntoView({ behavior: 'smooth' });
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while generating the recipe. Please try again.');

            // Hide loading indicator
            loadingIndicator.style.display = 'none';
            generateBtn.disabled = false;
        });
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
            const plainText = item.textContent;
            recipeText += plainText;
            if (index < ingredientsItems.length - 1) {
                recipeText += ", ";
            }
        });
        recipeText += ". ";

        // Add instructions
        recipeText += "Instructions: ";
        const instructionsItems = instructionsList.querySelectorAll('li');
        instructionsItems.forEach((item, index) => {
            // Get plain text content, removing any HTML tags and cleaning up whitespace
            const plainText = item.textContent.replace(/\s+/g, ' ').trim();
            recipeText += `Step ${index + 1}: ${plainText}. `;
        });

        // Make API call to generate audio
        fetch('/api/text-to-speech', {
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
            return response.json();
        })
        .then(data => {
            // Check if we have audio URLs
            if (!data.audio_urls || data.audio_urls.length === 0) {
                throw new Error('No audio URLs returned');
            }

            // Store the audio URLs in a global variable
            window.audioUrls = data.audio_urls;
            window.currentAudioIndex = 0;

            // Set up the audio player
            playNextAudioSegment();
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while generating the audio. Please try again.');

            // Hide loading indicator
            audioLoadingIndicator.style.display = 'none';
            playAudioBtn.disabled = false;
        });
    }

    // Function to play audio segments sequentially
    function playNextAudioSegment() {
        if (!window.audioUrls || window.currentAudioIndex >= window.audioUrls.length) {
            // All segments have been played
            audioLoadingIndicator.style.display = 'none';
            playAudioBtn.disabled = false;
            return;
        }

        // Set audio source to current segment
        recipeAudio.src = window.audioUrls[window.currentAudioIndex];

        // Show audio player
        recipeAudio.style.display = 'block';

        // Play audio
        recipeAudio.play();

        // Set up event listener for when this segment ends
        recipeAudio.onended = function() {
            // Move to the next segment
            window.currentAudioIndex++;
            playNextAudioSegment();
        };

        // If this is the first segment, hide loading indicator
        if (window.currentAudioIndex === 0) {
            audioLoadingIndicator.style.display = 'none';
            playAudioBtn.disabled = false;
        }
    }
});
