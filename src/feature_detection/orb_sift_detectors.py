import cv2


def extract_keypoints_and_descriptors(img_1_path, img_2_path, detector_type="ORB"):
    """
    Extracts keypoints and descriptors from two images.

    Args:
        img_1_path (str): Path to the first image.
        img_2_path (str): Path to the second image.
        detector_type (str): Feature detector to use ('ORB', 'SIFT'). Default is 'ORB'.

    Returns:
        tuple: A tuple containing keypoints and descriptors for both images:
            - keypoints_1, descriptors_1: Keypoints and descriptors of the first image.
            - keypoints_2, descriptors_2: Keypoints and descriptors of the second image.

    """

    img1 = cv2.imread(img_1_path, cv2.IMREAD_GRAYSCALE)
    img2 = cv2.imread(img_2_path, cv2.IMREAD_GRAYSCALE)

    if img1 is None or img2 is None:
        raise FileNotFoundError("One or both image paths are invalid or images cannot be read.")

    if detector_type == "ORB":
        detector = cv2.ORB_create(nfeatures=1000, nlevels=16)
    elif detector_type == "SIFT":
        detector = cv2.SIFT_create()
    else:
        raise ValueError(f"Unsupported detector type: {detector_type}. Use 'ORB' or 'SIFT'.")

    keypoints_1, descriptors_1 = detector.detectAndCompute(img1, None)
    keypoints_2, descriptors_2 = detector.detectAndCompute(img2, None)

    return (keypoints_1, descriptors_1), (keypoints_2, descriptors_2)


if __name__ == "__main__":
    TEST_IMGS_PATH = "test_imgs/"
    IMG_PATH_1 = TEST_IMGS_PATH + "cam1_1.jpg"
    IMG_PATH_2 = TEST_IMGS_PATH + "cam2_1.jpg"

    try:
        (kp1, d1), (kp2, d2) = extract_keypoints_and_descriptors(IMG_PATH_1, IMG_PATH_2, detector_type="ORB")

        print(f"Keypoints in image 1: {len(kp1)}")
        print(f"Keypoints in image 2: {len(kp2)}")

    except FileNotFoundError as e:
        print(e)
