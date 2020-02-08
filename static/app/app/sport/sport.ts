import { Component, OnInit, ElementRef } from '@angular/core';
import { platformBrowserDynamic } from '@angular/platform-browser-dynamic';
import { enableProdMode } from '@angular/core';
import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { HttpModule } from '@angular/http';
import { UsatuRpcService }     from '../usatu-rpc/usatu-rpc.service';
import { UsatuConfigService } from '../usatu-config/usatu-config.service';


@Component({
    moduleId: module.id,
    selector: 'sport',
    templateUrl: 'sport.html',
    styleUrls: [ 'sport.css' ]
})
export class VkAuthComponent implements OnInit {
    sid_token:string = null;
    user_name:string = null;
    vk_photo:string = null;

    // Страница конкретного пользователя
    member_id = null;
    user_info = null;

    // Страница соревнования
    challenge_id = null;
    challenge_info = null;

    challenges = [];
    current_cat = 'recommend';

    filters = [];

    actions = [
        {
            'name': 'registered',
            'img': 'reg.svg',
            'text': 'Точно участвую'
        },
        {
            'name': 'like',
            'img': 'heart.svg',
            'text': 'Слежу за событием'

        },
        {
            'name': 'delete',
            'img': 'block.svg',
            'text': 'Не буду участвовать'
        }
        // ,
        // {
        //     'name': 'sell',
        //     'img': 'sell.svg',
        //     'text': 'Продам слот'
        // }
    ]

    constructor(
            private rpcService: UsatuRpcService,
            private _config: UsatuConfigService,
            public elementRef: ElementRef
        ) {

        let native = this.elementRef.nativeElement;
        this.sid_token = native.getAttribute("sid-token");
        this.user_name = native.getAttribute("user-name");
        this.vk_photo = native.getAttribute("vk-photo");
        this.member_id = native.getAttribute("member-id");
        this.challenge_id = native.getAttribute("challenge-id");

        if (!this.member_id) {
            this.member_id = null;
        } else {
            this.member_id = parseInt(this.member_id, 10);
        }

        if (!this.challenge_id) {
            this.challenge_id = null;
        } else {
            this.challenge_id = parseInt(this.challenge_id, 10);
        }

        if (!this.sid_token) {
            this.sid_token = null;
        }

        if (!this.vk_photo) {
            this.vk_photo = null;
        }
    }

    isTabActive(cat) {
        return (this.current_cat == cat && !this.user_info && !this.challenge_id);
    }

    ngOnInit(): void {
        if (this.sid_token !== null) {
            this.setCookie(this.sid_token);
            document.location.href = this.get_domen_url();
            return;
        }

        this.getData();
    }

    setCookie(sid) {
        if (!sid) {
            return;
        }
        $.cookie('usatu_auth', sid, { expires : 365, path: '/' });
    }

    switch_category(cat) {
        this.user_info = null;
        this.member_id = null;

        this.challenge_id = null;
        this.challenge_info = null;

        this.current_cat = cat;
        this.getData();
    }

    addFilter(sport) {
        if (this.filters.indexOf(sport) == -1) {
            this.filters.push(sport);
            this.getData();
        } else {
            this.removeFilter(sport);
        }
    }

    removeFilter(sport) {
        let index = this.filters.indexOf(sport);
        if (index > -1) {
            this.filters.splice(index, 1);
            this.getData();
        }
    }

    getData() {
        if (this.member_id) {
            this.rpcService.call(
                'get_challenges_list',
                {
                    'category': 'user',
                    'member_id': this.member_id,
                    'filters': this.filters
                })
                    .then(res => this.challenges = res.challenges);

            // Request user info
            this.rpcService.call(
                'get_member_info',
                {
                    'member_id': this.member_id,
                })
                    .then(res =>
                        this.user_info = res.user_info
                    );

            return;
        } else if (this.challenge_id) {
            // Request challenge info
            this.rpcService.call(
                'get_challenge_info',
                {
                    'challenge_id': this.challenge_id,
                })
                    .then(res =>
                        this.challenge_info = res.challenge_info
                    );
            return;

        }

        this.rpcService.call(
            'get_challenges_list',
            {
                'category': this.current_cat,
                'filters': this.filters
            })
                .then(res => this.challenges = res.challenges);
    }

    get_challenge_part_type(challenge_id) {
        for (let ch of this.challenges) {
            if (ch.id == challenge_id) {
                return ch.part_type;
            }
        }
    }

    action(challenge_id, action_type) {
        // Save old status for restore
        let old_part_type = null;
        let is_set = true;

        for (let ch of this.challenges) {
            if (ch.id == challenge_id) {
                old_part_type = ch.part_type;

                if (old_part_type == action_type) {
                    is_set = false;
                    ch.part_type = null;
                } else {
                    // Set new status immediately
                    ch.part_type = action_type;
                }
                break;
            }
        }

        if (this.challenge_id === challenge_id) {
            old_part_type = this.challenge_info['part_type'];

            if (old_part_type == action_type) {
                is_set = false;
                this.challenge_info['part_type'] = null;
            } else {
                // Set new status immediately
                this.challenge_info['part_type'] = action_type;
            }
        }

        this.rpcService.call(
            'challenge_action',
            {
                'id': challenge_id,
                'action': action_type,
                'is_set': is_set
            })
                .then(res =>
                    this.handlerSetPartType(res, challenge_id, old_part_type)
                );
    }


    handlerSetPartType(res, challenge_id, old_part_type) {
        if (!!res.sid) {
            this.setCookie(res.sid);
        }

        if (!res.challenge_id) {
            // If update failed - return participation type back
            this.set_challenge_part_type(challenge_id, old_part_type);
        }
    }


    set_challenge_part_type(challenge_id, action_type) {
        for (let ch of this.challenges) {
            if (ch.id == challenge_id) {
                ch.part_type = action_type;
                return;
            }
        }

        if (this.challenge_id === challenge_id) {
            this.challenge_info['part_type'] = action_type;
        }
    }


    addFriend(friend_id) {
        let new_status = 'friend';
        if (this.user_info.friend_status == 'friend') {
            new_status = null;
        }

        this.rpcService.call('set_friend_status',{
            'friend_id': friend_id,
            'status': new_status
        }).then(res => {
            this.user_info.friend_status = res.friend_status;
            this.setCookie(res.sid);
        });
    }

    friendButtonText() {
        if (this.user_info.friend_status == 'friend') {
            return 'Удалить из друзей';
        } else {
            return 'Добавить в друзья';
        }
    }

    open_vk(): void {
        let scope = 'friends';
        scope += ',offline';
        let url = (
            'https://oauth.vk.com/authorize?' +
            'client_id=' + this._config.config().VK_APP_ID +
            '&display=page' +
            '&redirect_uri=' + this.get_domen_url() +
            '&scope=' + scope +
            '&response_type=code' +
            '&v=5.103'
        );
        document.location.href = url;
    }

    get_domen_url(): string {
        let domen = this._config.config().SPORT_DOMEN;
        let root = this._config.config().SPORT_ROOT_PATH;
        let url = 'http://' + domen;
        if (root) {
            url += '/' + root;
        }
        return url
    }


    get_russian(sport): string {
        let lang = {
            'ski': 'лыжи',
            'skyrunning': 'скайраннинг',
            'run': 'бег',
            'trail': 'трайл',
            'swim': 'плавание',
            'triathlon': 'триатлон',
            'bicycle': 'велосипед'
        };
        return lang[sport] || sport;
    }

    showEmptyListMessage(): boolean {
        return (
            !this.challenge_id &&
            !this.member_id &&
            this.challenges.length == 0 &&
            this.current_cat == 'friends'
        );
    }

    showEmptyListMyMessage(): boolean {
        return (
            !this.challenge_id &&
            !this.member_id &&
            this.challenges.length == 0 &&
            this.current_cat == 'my'
        );
    }
}

@NgModule({
    imports: [
        BrowserModule,
        HttpModule
    ],
    declarations: [VkAuthComponent],
    providers: [UsatuRpcService, UsatuConfigService],
    bootstrap: [VkAuthComponent]
})
export class VkAuthModule { }

let conf = new UsatuConfigService();
if (conf.config().enableProdMode()) {
    enableProdMode();
}

platformBrowserDynamic().bootstrapModule(VkAuthModule);
