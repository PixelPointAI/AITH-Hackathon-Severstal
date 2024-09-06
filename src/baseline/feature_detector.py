import cv2

def extract_keypoints_and_descriptors(image_path_1, image_path_2, detector_type='ORB'):
    """
    Extracts keypoints and descriptors from two images.
    
    Args:
        image_path_1 (str): Path to the first image (left image from stereo camera).
        image_path_2 (str): Path to the second image (right image from stereo camera).
        detector_type (str): Feature detector to use ('ORB', 'SIFT'). Default is 'ORB'.
    
    Returns:
        tuple: A tuple containing keypoints and descriptors for both images:
            - keypoints_1, descriptors_1: Keypoints and descriptors of the first image.
            - keypoints_2, descriptors_2: Keypoints and descriptors of the second image.
    """

    img1 = cv2.imread(image_path_1, cv2.IMREAD_GRAYSCALE)
    img2 = cv2.imread(image_path_2, cv2.IMREAD_GRAYSCALE)

    if img1 is None or img2 is None:
        raise FileNotFoundError("One or both image paths are invalid or images cannot be read.")

    if detector_type == 'ORB':
        detector = cv2.ORB_create(nfeatures=1000, nlevels=16)
    elif detector_type == 'SIFT':
        detector = cv2.SIFT_create()
    else:
        raise ValueError(f"Unsupported detector type: {detector_type}. Use 'ORB', 'SIFT', or 'SURF'.")

    keypoints_1, descriptors_1 = detector.detectAndCompute(img1, None)
    keypoints_2, descriptors_2 = detector.detectAndCompute(img2, None)

    return (keypoints_1, descriptors_1), (keypoints_2, descriptors_2)


if __name__ == "__main__":
    test_imgs_path = 'test_imgs/'
    image_path_1 = test_imgs_path + 'cam1_1.jpg'
    image_path_2 = test_imgs_path + 'cam2_1.jpg'

    try:
        (keypoints_1, descriptors_1), (keypoints_2, descriptors_2) = extract_keypoints_and_descriptors(image_path_1, 
                                                                                                       image_path_2, 
                                                                                                       detector_type='ORB')

        print(f"Keypoints in image 1: {len(keypoints_1)}")
        print(f"Keypoints in image 2: {len(keypoints_2)}")

    except FileNotFoundError as e:
        print(e)
    except Exception as e:
        print(f"An error occurred: {e}")
