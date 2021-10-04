document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".like").forEach((heart) => {
    heart.addEventListener("click", (event) => update_count(event));
  });
  document.querySelectorAll(".loginToLike").forEach((heart) => {
    heart.addEventListener("click", (event) => {
      event.preventDefault();
      alert("You need to be logged in to like posts");
    });
  });
  document.querySelectorAll(".edit").forEach((editlink) => {
    editlink.addEventListener("click", (event) => edit_post(event));
  });
  document.querySelectorAll(".edit_form").forEach((editlink) => (editlink.style.display = "none"));
  document.querySelectorAll(".delete").forEach((deleteButton) => {
    deleteButton.addEventListener("click", (event) => delete_post(event));
  });
});

function delete_post(event) {
  //Prevent reloading the page after clicking on the "delete" link
  event.preventDefault();

  let postID = event.target.dataset.postid;
  let postBlock = document.querySelector(`#postBlock${postID}`);

  let confirm = prompt("Are you sure you want to delete this post? (y / n)");
  if (confirm === "y") {
    fetch(`/posts/${postID}`, {
      method: "DELETE",
    }).then((response) => {
      postBlock.innerHTML = "This post has been deleted";
    });
  } else if (confirm === "n") {
    alert("Ok, we'll keep the post where it is");
  } else {
    alert("Sorry, we didn't understand if this post should be deleted. Please try again.");
  }
}

function update_post(event) {
  //Prevent reloading the page after form submission
  event.preventDefault();

  let postID = event.target.dataset.postid;
  let editLink = document.querySelector(`#editPost${postID}`);
  let postBlock = document.querySelector(`#postBlock${postID}`);
  let postContent = document.querySelector(`#postContent${postID}`);

  //Get the updated content of the post edited by the author
  let updatedPost = document.querySelector(`#editContent${postID}`).value;

  //Update the post content using internal API
  fetch(`/posts/${postID}`, {
    method: "PUT",
    body: JSON.stringify({
      content: updatedPost,
    }),
  }).then((response) => {
    //Display the updated post details on the page
    postBlock.style.display = "block";
    postContent.innerHTML = updatedPost;
    editLink.style.display = "none";
  });
}

function edit_post(event) {
  //Prevent reloading the page after a click on the "edit" link
  event.preventDefault();

  let postID = event.target.dataset.postid;
  let editLink = document.querySelector(`#editPost${postID}`);
  let postBlock = document.querySelector(`#postBlock${postID}`);

  //Display the form for editing the post in place of the post details
  postBlock.style.display = "none";
  editLink.style.display = "block";

  //Attach event listener to the form that allows the user to edit the post
  editLink.addEventListener("submit", (event) => update_post(event));
}

function update_count(event) {
  //Prevent reloading the page after a click on the "heart"
  event.preventDefault();

  //Get the id of the relevant post
  let postID = event.target.dataset.postid;

  let addLiker;

  //Get the username of the logged in user
  let user = document.querySelector("#userID").innerHTML;

  function update_status(addLikerBool, heartSymbol, updatedNumLikes) {
    addLiker = addLikerBool;
    event.target.innerHTML = heartSymbol;
    document.querySelector(`#postLikes${postID}`).innerHTML = updatedNumLikes;
  }

  //Get the details of the post via internal API
  fetch(`/posts/${postID}`)
    .then((response) => response.json())
    .then((postDetails) => {
      /* check if the logged in user should be added to the list of those who liked the post,
      then update the heart symbol and the number of likes accordingly */
      if (!postDetails.likedBy.includes(user)) {
        update_status(true, "❤️", postDetails.likedBy.length + 1);
      } else {
        update_status(false, "♡", postDetails.likedBy.length - 1);
      }
    })
    .then(() => {
      //Update the list of users who liked the post via internal API
      fetch(`/posts/${postID}`, {
        method: "PUT",
        body: JSON.stringify({
          likedBy: user,
          addLiker: addLiker,
        }),
      });
    });
}
