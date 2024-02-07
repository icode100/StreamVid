import React from 'react';
import ReactPlayer from 'react-player';

const VideoPlayer = ({ url, overlays }) => {
  return (
    <div>
      <ReactPlayer
        url={url}
        playing
        controls
        muted // Use muted prop if overlays cover full video
        width="100%"
        height="auto"
        render={(props) => <video {...props} style={{ position: 'relative' }} />} // Allow overlay positioning
      >
        {overlays.map((overlay) => (
          <div key={overlay.id} style={{ ...overlay.style }}>{overlay.content}</div>
        ))}
      </ReactPlayer>
    </div>
  );
};

export default VideoPlayer;
