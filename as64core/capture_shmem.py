import mmap
import ctypes
import numpy as np

# Constants
FILE_MAP_READ = 0x0004
PAGE_READWRITE = 0x04
SHMEM_NAME = "as64_grabber"

class SharedMemoryCapture(object):
    def __init__(self):
        self.shmem_handle = None
        self.shmem = None
        self.width = 0
        self.height = 0
        self.linesize = 0
        self.shmem_size = 0

    def open_shmem(self):
        # Check if shared memory is already open
        if self.shmem_handle:
            return True
        """Open the shared memory connection"""
        self.shmem_handle = ctypes.windll.kernel32.OpenFileMappingW(FILE_MAP_READ, False, SHMEM_NAME)
        if not self.shmem_handle:
            raise Exception("Could not open shared memory")
        
        # Read initial header to set up first mapping
        self._update_dimensions()
        self.shmem = mmap.mmap(-1, self.shmem_size, tagname=SHMEM_NAME, access=mmap.ACCESS_READ)
        print("Shared memory opened")
        return True

    def close_shmem(self):
        """Close the shared memory connection"""
        # if self.shmem:
        #     self.shmem.close()
        if self.shmem_handle:
            ctypes.windll.kernel32.CloseHandle(self.shmem_handle)
            self.shmem_handle = None
            print("Shared memory closed")

    def _update_dimensions(self):
        """Read header and update dimensions"""
        
        # Check if shared memory is open of not, open it
        if not self.shmem_handle:
            self.open_shmem()
        shmem_header = mmap.mmap(-1, 16, tagname=SHMEM_NAME)
        shmem_header.seek(0)
        header = np.frombuffer(shmem_header.read(16), dtype=np.uint32)
        shmem_header.close()

        new_width = header[0]
        new_height = header[1]
        new_linesize = header[2]

        if (new_width != self.width or 
            new_height != self.height or 
            new_linesize != self.linesize):
            
            self.width = new_width
            self.height = new_height
            self.linesize = new_linesize
            self.shmem_size = 16 + self.height * self.linesize

            if self.shmem:
                self.shmem.close()
                self.shmem = mmap.mmap(-1, self.shmem_size, tagname=SHMEM_NAME, access=mmap.ACCESS_READ)

    def get_capture_size(self):
        """Get the current capture dimensions"""
        self._update_dimensions()
        # Return width and height as int tuple
        return int(self.width), int(self.height)

    def capture(self):
        """Capture a single frame from shared memory"""
        self._update_dimensions()
        
        if not self.shmem:
            raise Exception("Shared memory not initialized")

        self.shmem.seek(0)
        data = self.shmem.read(self.shmem_size)
        
        # Convert the data to a numpy array
        return np.frombuffer(data, dtype=np.uint8, offset=16).reshape((self.height, self.width, 3))

def test_capture():
    """Test function to demonstrate shared memory capture with OpenCV visualization"""
    import cv2
    
    # Initialize capture
    cap = SharedMemoryCapture()
    try:
        cap.open_shmem()
        width, height = cap.get_capture_size()
        print(f"Capture size: {width}x{height}")
        
        cv2.namedWindow("Capture Test", cv2.WINDOW_NORMAL)
        frame = None
        
        while True:
            key = cv2.waitKey(1) & 0xFF
            
            # Capture new frame when 'w' is pressed
            if key == ord('w'):
                frame = cap.capture()
                print("New frame captured")
            
            # Display the last captured frame if available
            if frame is not None:
                cv2.imshow("Capture Test", frame)
            
            # Break if 'q' is pressed
            if key == ord('q'):
                break
                
    finally:
        cv2.destroyAllWindows()
        cap.close_shmem()

if __name__ == "__main__":
    test_capture()