const Banner = document.querySelector('.banner');
const BannerUpload = document.querySelector('#banner-upload');

let bannerPath;
BannerUpload.addEventListener('change', ()=>{
    uploadImage(BannerUpload,"Banner");
})

Banner.style.backgroundImage = `url(${getFile()})`;  // Corrected typo here

const uploadImage = (uploadFile, uploadType) =>{
    const [file] = uploadFile.files;
    if (file && file.type.includes("image")) {
        const formData = new FormData();
        formData.append('image', file);

        fetch('/uploads', {  // Make sure this URL is correct
            method: 'POST',
            body: formData
        })
        .then(res => res.json())
        .then(data => {
            if (data.path) {
                if (uploadType =="image") {
                    addImage(data.path,file.name)
                }
                else{   
                    bannerPath = `${location.origin}/${data.path}`;
                    storeFile(bannerPath);
                    Banner.style.backgroundImage = `url(${getFile()})`;  // Corrected typo here
                }
                
            } else {
                alert(data.message);  // Handle error
            }
        })
        .catch(error => {
            console.error('Error uploading image:', error);
            alert('Image upload failed');
        });
    } else {
        alert('Please upload a valid image file');
    }
}

function storeFile(url) {
    sessionStorage.setItem('uploadedFile', url);
}

function getFile() {
    return sessionStorage.getItem('uploadedFile');
}
