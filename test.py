import matplotlib.pyplot as plt
import cv2

def dilate_image(image, scale_x, scale_y):
    height, width = image.shape[:2]
    dilated = cv2.resize(image, (int(width * scale_x), int(height * scale_y)))
    return dilated


if __name__ == "__main__":
    image = cv2.imread("image.jpg")
    dilated_image = dilate_image(image, 0.2, 0.2)
    
    output_path = "image_low.jpg"
    cv2.imwrite(output_path, dilated_image)
    
    plt.subplot(1, 2, 1)
    plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    plt.title("Original Image")
    plt.axis("off")

    plt.subplot(1, 2, 2)
    plt.imshow(cv2.cvtColor(dilated_image, cv2.COLOR_BGR2RGB))
    plt.title("Dilated Image")
    plt.axis("off")

    plt.tight_layout()
    plt.show()