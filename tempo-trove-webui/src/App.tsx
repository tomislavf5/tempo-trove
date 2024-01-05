import axios from 'axios';
import { useEffect, useState, useRef } from 'react';

interface Autocomplete {
  _id: string;
  name: string;
  album: string;
}

let timeout: number;

function App() {
  const [suggestions, setSuggestions] = useState<Autocomplete[]>([]);
  const [selectedTracks, setSelectedTracks] = useState<Autocomplete[]>([]);
  const [search, setSearch] = useState<string>('');
  const [showSuggestions, setShowSuggestions] = useState<boolean>(false);

  const searchRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const loadSuggestions = async () => {
      const response = await axios.get<Autocomplete[]>(
        'http://127.0.0.1:8000/search/?search=' + search
      );
      setSuggestions(response.data);
    };
    loadSuggestions();
  }, [search]);

  const onSearchChange = (searchText: string): void => {
    clearTimeout(timeout);
    timeout = setTimeout(() => {
      setSearch(searchText);
    }, 300);
  };

  const onInputBlur = () => {
    setTimeout(() => {
      setShowSuggestions(false);
    }, 100);
  };

  const onSelectTrack = (selectedMovie: Autocomplete) => {
    searchRef.current!.value = '';
    setSearch('');
    if (selectedTracks.find((movie) => movie._id === selectedMovie._id)) {
      return;
    }
    setSelectedTracks([
      ...selectedTracks,
      { _id: selectedMovie._id, name: selectedMovie.name , album: selectedMovie.album},
    ]);
  };

  const onDeselectTrack = (movieToRemove: Autocomplete) => {
    setSelectedTracks(
      selectedTracks.filter((movie) => movie._id !== movieToRemove._id)
    );
  };

  return (
    <>
      <h1 className="text-center mt-4 font-bold text-2xl">
        Tempo Trove
      </h1>
      <div className="h-full p-10 flex justify-center">
        <div className="flex gap-10">
          <div className="w-80 h-[80%]">
            <label htmlFor="searchInput">Track name</label>
            <input
              type="text"
              id="searchInput"
              className="border-gray border-2 w-full"
              onChange={(e) => onSearchChange(e.target.value)}
              onFocus={() => setShowSuggestions(true)}
              onBlur={() => onInputBlur()}
              ref={searchRef}
            />
            <div className="bg-gray-200">
              {suggestions &&
                showSuggestions &&
                suggestions.map((suggestion) => (
                  <p
                    key={suggestion._id}
                    className="cursor-pointer hover:bg-gray-300 w-full text-center"
                    onClick={() => onSelectTrack(suggestion)}
                  >
                    {suggestion.name} - {suggestion.album}
                  </p>
                ))}
            </div>
          </div>
          <div>
            {selectedTracks &&
              selectedTracks.map((track) => (
                <p
                  key={track._id}
                  className="cursor-pointer hover:bg-red-300"
                  onClick={() => onDeselectTrack(track)}
                >
                  {track.name}
                </p>
              ))}
          </div>
          {selectedTracks?.length > 0 && (
            <div>
              <button
                className="bg-blue-300 p-2 rounded-full"
                onClick={() => {}} //TODO fetch reccommendations here
              >
                Fetch suggestions
              </button>
            </div>
          )}
        </div>
      </div>
    </>
  );
}

export default App;
