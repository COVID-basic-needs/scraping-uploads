function getDateTimeNow() {
  // get current datetime in yyyy/mm/dd HH/mm/ss

  const date = new Date();
  const aaaa = date.getFullYear();
  let gg = date.getDate();
  let mm = (date.getMonth() + 1);

  if (gg < 10) gg = `0${gg}`;

  if (mm < 10) mm = `0${mm}`;

  const cur_day = `${aaaa}-${mm}-${gg}`;

  let hours = date.getHours();
  let minutes = date.getMinutes();
  let seconds = date.getSeconds();

  if (hours < 10) hours = `0${hours}`;

  if (minutes < 10) minutes = `0${minutes}`;

  if (seconds < 10) seconds = `0${seconds}`;

  return `${cur_day} ${hours}:${minutes}:${seconds}`;
}

module.exports = {
  getDateTimeNow,
};
