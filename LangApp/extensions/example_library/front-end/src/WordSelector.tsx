import { useDynamicProperty } from "taipy-gui";
import React, { useState, useEffect } from 'react';

import './WordSelector.css'; // Import the CSS file

const DATABASE_URL = 'http://127.0.0.1:5001/words';

const saveWordToDatabase = async (word: string, id: string): Promise<void> => {
  try {
    console.log('Sending request with payload:', { sessionId: id, word });
    const response = await fetch(`${DATABASE_URL}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        sessionId: id,
        word: word,
      }),
    });

    if (!response.ok) {
      const errorMessage = await response.text();
      console.error('Backend returned an error:', errorMessage);
      throw new Error(`Failed to save word: ${response.statusText}`);
    }

    const data = await response.json();
    console.log('Backend response:', data);
  } catch (error) {
    console.error('Error in saveWordToDatabase:', error);
  }
};

interface WordSelectorProps {
  textbody?: string;
  defaultTextbody?: string;
  sessionid?: string;
  defaultSessionid?: string;
}

interface Selected {
  id: number;
  sessionId: string;
  word: string;
}

const WordSelector: React.FC<WordSelectorProps> = (props) => {
  const text = useDynamicProperty(props.textbody, props.defaultTextbody, "");
  const sessionid = useDynamicProperty(props.sessionid, props.defaultSessionid, "");

  if (!text) {
    return <p>No text provided</p>;
  }

  if (!sessionid) {
    return <p>No sessionid provided</p>;
  }

  // Split the text into words
  const words = text.split(' ');

  // State to store selected words to bold
  const [selectedWords, setSelectedWords] = useState<string[]>([]);

  const handleDoubleClick = async (word: string, id: string): Promise<void> => {
    console.log('Double-clicked word:', word);
    try {
      // Save the word and wait for it to complete
      await saveWordToDatabase(word, id);

      // Fetch the latest words after the word is saved
      await fetchWords(sessionid);

      // Update bolding state after fetching the words
      setSelectedWords((prevSelectedWords) =>
        prevSelectedWords.includes(word) ? prevSelectedWords : [...prevSelectedWords, word]
      );
    } catch (error) {
      console.error('Error in handleDoubleClick:', error);
    }
  };

  const [selected, setSelected] = useState<Selected[]>([]);

  useEffect(() => {
    fetchWords(sessionid);
  }, [sessionid]);

  const fetchWords = async (id: string | null): Promise<Selected[]> => {
    try {
      let url = `${DATABASE_URL}`;
      if (id) {
        url += `?sessionId=${id}`;
      }

      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`Error fetching words: ${response.statusText}`);
      }

      const data = await response.json();
      console.log('Fetched words from backend:', data.words); // Debugging output
      setSelected(data.words || []); // Update the state with fetched words
      return data.words || [];
    } catch (error) {
      console.error('Error fetching words:', error);
      return [];
    }
  };

  const paragraphs = text.split('\n');

  return (
    <div className="text-container">
      {paragraphs.map((paragraph, pIndex) => (
        <p key={pIndex} className="paragraph">
          {paragraph.split(' ').map((word, wIndex) => (
            <span
              key={wIndex}
              className="word"
              onDoubleClick={() => handleDoubleClick(word, sessionid)}
              style={{
                fontWeight: selectedWords.includes(word) ? 'bold' : 'normal',
              }}
            >
              {word}{' '}
            </span>
          ))}
        </p>
      ))}
    </div>
  );


//   return (
//     <>
//       <h2>Text Body</h2>
//       <div className="text-container">
//         {words.map((word, index) => (
//           <span
//             key={index}
//             className="word"
//             onDoubleClick={() => handleDoubleClick(word, sessionid)}
//             style={{
//               fontWeight: selectedWords.includes(word) ? 'bold' : 'normal',
//             }}
//           >
//             {word}{' '}
//           </span>
//         ))}
//       </div>
//     </>
//   );
};

export default WordSelector;

